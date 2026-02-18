import io
import pytest
from bson import ObjectId

from app.core.services.user_service import UserService
from app.core.domain.models.user import User
from app.core.domain.models.image import UploadedImage
from app.core.errors.auth import PasswordDontMatchError
from app.core.errors.validation import (
    PasswordValidationError,
    UsernameValidationError,
    ImageExtensionValidationError,
    ImageNotFoundError,
)
from app.core.errors.user import (
    AbsentUserError,
    DeleteImageError,
    ImageUploadError,
)


# ---------------------- HELPERS ----------------------

def make_upload_file(name: str, data: bytes):
    """Минимальный объект 'файла' с интерфейсом UploadFile: filename и async read()."""
    class _DummyUploadFile:
        def __init__(self, n: str, d: bytes):
            self.filename = n
            self._data = d

        async def read(self) -> bytes:
            return self._data

    return _DummyUploadFile(name, data)


# ---------------------- ФЕЙКИ ----------------------

class FakeValidator:
    async def validate_password(self, pwd: str) -> bool:
        # считаем слабым ровно "weak"
        return pwd != "weak"

    async def validate_username(self, username: str) -> bool:
        # запрещаем юзернейм, заканчивающийся на "!"
        return not username.endswith("!")

    async def validate_image_extension(self, file) -> bool:
        # проверяем только расширение имени файла
        return str(file.filename).lower().endswith((".jpg", ".jpeg", ".png", ".tif", ".tiff"))


class FakeSecurity:
    def hash_password(self, password: str):
        return ("SALT", "HASH")

    def serialize_hash(self, salt: str, hash_: str):
        return f"{salt}:{hash_}"


class FakeStorage:
    """Эмуляция MinioGateway: put_object / delete_file и client.meta.endpoint_url."""
    _bucket = "bucket"

    class ClientMeta:
        endpoint_url = "http://minio.test"

    class Client:
        def __init__(self):
            self.meta = FakeStorage.ClientMeta()

    def __init__(self):
        self._client = self.Client()
        self.put_calls: list[str] = []
        self.delete_calls: list[str] = []

    def put_object(self, object_name, data: io.BytesIO, size: int):
        # если в данных встретится "fail", эмулируем ошибку загрузки
        if b"fail" in data.getvalue():
            raise Exception("upload fail")
        self.put_calls.append(object_name)

    def delete_file(self, filename: str):
        # если имя специально "плохое", эмулируем ошибку удаления
        if filename.startswith("bad"):
            raise Exception("delete fail")
        self.delete_calls.append(filename)


class FakeUserRepo:
    """Фейковый репозиторий пользователей."""
    def __init__(self):
        self.users: dict[ObjectId, dict] = {}

    async def add(self, data: dict):
        _id = ObjectId()
        self.users[_id] = {**data, "_id": _id}
        return _id

    async def get_one(self, query: dict):
        if "_id" in query:
            return self.users.get(query["_id"])
        if "email" in query:
            for u in self.users.values():
                if u["email"] == query["email"]:
                    return u
        if "username" in query:
            for u in self.users.values():
                if u["username"] == query["username"]:
                    return u
        return None


class FakeImageRepo:
    """Фейковый репозиторий изображений."""
    def __init__(self):
        self.images: dict[ObjectId, dict] = {}

    async def add(self, data: dict):
        _id = ObjectId()
        self.images[_id] = {**data, "_id": _id}
        return _id

    async def get_one(self, query: dict):
        if "_id" in query:
            return self.images.get(query["_id"])
        if "url" in query:
            for img in self.images.values():
                if img["url"] == query["url"]:
                    return img
        return None

    async def get_many(self, query: dict, limit: int):
        if "_user_id" in query:
            res = [img for img in self.images.values() if img["_user_id"] == query["_user_id"]]
            return res[:limit]
        return []

    async def delete(self, query: dict):
        to_delete = None
        for k, v in self.images.items():
            if v["url"] == query["url"]:
                to_delete = k
                break
        if to_delete is not None:
            del self.images[to_delete]
        else:
            raise Exception("not found")


# ---------------------- ТЕСТЫ МОДУЛЯ UserService ----------------------

@pytest.mark.asyncio
class TestUserServiceModule:
    @pytest.fixture
    def setup_service(self):
        user_repo = FakeUserRepo()
        image_repo = FakeImageRepo()
        storage = FakeStorage()
        service = UserService(
            user_repo=user_repo,
            image_repo=image_repo,
            security=FakeSecurity(),
            validator=FakeValidator(),
            storage=storage,
        )
        return service, user_repo, image_repo, storage

    # ---- CREATE USER ----

    async def test_create_user_success(self, setup_service):
        service, user_repo, image_repo, _ = setup_service
        user = await service.create_user("John", "john@example.com", "pwd", "pwd")
        assert isinstance(user, User)
        assert user.username == "John"
        assert user.email == "john@example.com"
        assert len(user_repo.users) == 1

    async def test_create_user_passwords_mismatch(self, setup_service):
        service, *_ = setup_service
        with pytest.raises(PasswordDontMatchError):
            await service.create_user("John", "john@example.com", "a", "b")

    async def test_create_user_weak_password(self, setup_service):
        service, *_ = setup_service
        with pytest.raises(PasswordValidationError):
            await service.create_user("John", "john@example.com", "weak", "weak")

    async def test_create_user_bad_username(self, setup_service):
        service, *_ = setup_service
        with pytest.raises(UsernameValidationError):
            await service.create_user("John!", "john@example.com", "pwd", "pwd")

    # ---- UPLOAD IMAGE ----

    async def test_upload_image_success(self, setup_service):
        service, user_repo, image_repo, storage = setup_service
        user = await service.create_user("John", "john@example.com", "pwd", "pwd")

        file = make_upload_file("photo.jpg", b"some image bytes")
        uploaded = await service.upload_image(str(user.id), file)

        assert isinstance(uploaded, UploadedImage)
        assert uploaded.url.startswith("http://minio.test")
        assert len(image_repo.images) == 1
        assert len(storage.put_calls) == 1

    async def test_upload_image_bad_extension(self, setup_service):
        service, *_ = setup_service
        user = await service.create_user("John", "john@example.com", "pwd", "pwd")

        file = make_upload_file("photo.txt", b"123")
        with pytest.raises(ImageExtensionValidationError):
            await service.upload_image(str(user.id), file)

    async def test_upload_image_storage_fail(self, setup_service):
        service, *_ = setup_service
        user = await service.create_user("John", "john@example.com", "pwd", "pwd")

        file = make_upload_file("photo.jpg", b"fail")
        with pytest.raises(ImageUploadError):
            await service.upload_image(str(user.id), file)



    async def test_get_all_user_images(self, setup_service):
        service, _, image_repo, _ = setup_service
        user = await service.create_user("John", "john@example.com", "pwd", "pwd")

        file = make_upload_file("photo.jpg", b"img")
        await service.upload_image(str(user.id), file)

        imgs = await service.get_all_user_images(str(user.id))
        assert isinstance(imgs, list)
        assert len(imgs) == 1
        assert isinstance(imgs[0], UploadedImage)



    async def test_delete_image_success(self, setup_service):
        service, _, image_repo, storage = setup_service
        user = await service.create_user("John", "john@example.com", "pwd", "pwd")

        file = make_upload_file("photo.jpg", b"data")
        uploaded = await service.upload_image(str(user.id), file)

        await service.delete_image(uploaded.url, str(user.id))
        assert len(image_repo.images) == 0
        assert len(storage.delete_calls) == 1

    async def test_delete_image_wrong_user(self, setup_service):
        service, user_repo, image_repo, _ = setup_service
        user1 = await service.create_user("John", "john@example.com", "pwd", "pwd")
        user2 = await service.create_user("Kate", "kate@example.com", "pwd", "pwd")

        file = make_upload_file("photo.jpg", b"data")
        uploaded = await service.upload_image(str(user1.id), file)

        with pytest.raises(DeleteImageError):
            await service.delete_image(uploaded.url, str(user2.id))

    async def test_delete_image_absent_user(self, setup_service):
        service, *_ = setup_service
        with pytest.raises(AbsentUserError):
            await service.delete_image("http://minio.test/bucket/img.jpg", str(ObjectId()))

    async def test_delete_image_not_found(self, setup_service):
        service, *_ = setup_service
        user = await service.create_user("John", "john@example.com", "pwd", "pwd")

        with pytest.raises(ImageNotFoundError):
            await service.delete_image("http://minio.test/bucket/notfound.jpg", str(user.id))

    async def test_delete_image_storage_fail(self, setup_service):
        service, _, image_repo, _ = setup_service
        user = await service.create_user("John", "john@example.com", "pwd", "pwd")

        file = make_upload_file("photo.jpg", b"ok")
        uploaded = await service.upload_image(str(user.id), file)

        # Меняем URL так, чтобы имя файла начиналось с "bad" → эмуляция сбоя delete_file()
        uploaded.url = "http://minio.test/bucket/badfile.jpg"

        # Обновляем запись в репозитории
        for img in image_repo.images.values():
            img["url"] = uploaded.url

        with pytest.raises(DeleteImageError):
            await service.delete_image(uploaded.url, str(user.id))

