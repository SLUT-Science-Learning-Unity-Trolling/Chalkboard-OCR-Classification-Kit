import asyncio
import pytest

from types import SimpleNamespace

# ВАЖНО: путь импорта должен соответствовать твоей структуре проекта.
# По присланным путям файлы лежат в app/core/services/.
from app.core.services.auth_service import AuthService
from app.api.schemas.user_dto import UserDTO
from app.core.errors.auth import InvalidEmailOrPasswordError


@pytest.mark.asyncio
class TestAuthService:
    # ----- ФИКСТУРЫ -----

    @pytest.fixture
    def fake_security(self):
        """
        Простой фейковый SecurityService.
        Сделан под ожидания AuthService: deserialize_hash -> (hash, salt).
        """
        class FakeSecurity:
            def deserialize_hash(self, data: str) -> tuple[str, str]:
                # Для теста вернём заранее "известные" значения
                return ("HASH123", "SALT123")

            def verify_hash(self, password: str, salt: str, hash_: str) -> bool:
                # Считаем верным только пароль "correct" и ровно эти hash/salt
                return password == "correct" and salt == "SALT123" and hash_ == "HASH123"

        return FakeSecurity()

    @pytest.fixture
    def fake_repo_user_ok(self):
        """
        Репозиторий, который возвращает одного пользователя по email/username.
        """
        class FakeRepo:
            def __init__(self):
                self._user = {
                    "_id": "6566b2c9f1a2b3c4d5e6f7a8",
                    "username": "john",
                    "email": "john@example.com",
                    "password_hash": "SERIALIZED",
                }

            async def get_one(self, query: dict):
                if query.get("email") == "john@example.com" or query.get("username") == "john":
                    return self._user
                return None

        return FakeRepo()

    @pytest.fixture
    def fake_repo_empty(self):
        class FakeRepo:
            async def get_one(self, query: dict):
                return None
        return FakeRepo()

    @pytest.fixture
    def patch_jam(self, monkeypatch):
        """
        Патчим jam внутри модуля AuthService.
        Нужны функции: make_payload, gen_jwt_token, verify_jwt_token.
        """
        def make_payload(exp, data):
            # Возвращаем то, что потом код передаст в gen_jwt_token
            return {"exp": exp, "data": data}

        def gen_jwt_token(payload):
            return "JWT.TOKEN.OK"

        def verify_jwt_token(token, check_exp=True, check_list=False):
            if token == "bad":
                raise ValueError("bad token")
            # Возвращаем полезную нагрузку с user_id
            return {"data": {"user_id": "6566b2c9f1a2b3c4d5e6f7a8"}}

        monkeypatch.setattr("app.core.services.auth_service.jam", SimpleNamespace(
            make_payload=make_payload,
            gen_jwt_token=gen_jwt_token,
            verify_jwt_token=verify_jwt_token,
        ))

    # ----- ТЕСТЫ auth_existing_user -----

    @pytest.mark.usefixtures("patch_jam")
    async def test_auth_by_email_success(self, fake_repo_user_ok, fake_security):
        service = AuthService(repository=fake_repo_user_ok, security=fake_security)
        user_dto, token = await service.auth_existing_user("john@example.com", "correct")

        assert isinstance(user_dto, UserDTO)
        assert user_dto.id == "6566b2c9f1a2b3c4d5e6f7a8"
        assert user_dto.username == "john"
        assert user_dto.email == "john@example.com"
        assert token == "JWT.TOKEN.OK"

    @pytest.mark.usefixtures("patch_jam")
    async def test_auth_by_username_success(self, fake_repo_user_ok, fake_security):
        service = AuthService(repository=fake_repo_user_ok, security=fake_security)
        user_dto, token = await service.auth_existing_user("john", "correct")

        assert user_dto.username == "john"
        assert token == "JWT.TOKEN.OK"

    async def test_auth_user_not_found(self, fake_repo_empty, fake_security):
        service = AuthService(repository=fake_repo_empty, security=fake_security)
        with pytest.raises(InvalidEmailOrPasswordError):
            await service.auth_existing_user("ghost@example.com", "whatever")

    @pytest.mark.usefixtures("patch_jam")
    async def test_auth_wrong_password(self, fake_repo_user_ok, fake_security):
        service = AuthService(repository=fake_repo_user_ok, security=fake_security)
        with pytest.raises(InvalidEmailOrPasswordError):
            await service.auth_existing_user("john", "wrong")

    # ----- ТЕСТЫ get_current_user -----

    @pytest.mark.usefixtures("patch_jam")
    async def test_get_current_user_success(self, fake_repo_user_ok):
        # Контейнер, который возвращает фейковый UserService с get_user_by_id
        class FakeUserService:
            async def get_user_by_id(self, user_id: str):
                return {"_id": "6566b2c9f1a2b3c4d5e6f7a8", "username": "john", "email": "john@example.com"}

        class FakeContainer:
            def resolve(self, cls):
                assert cls.__name__ == "UserService"
                return FakeUserService()

        class Req:
            def __init__(self):
                self.cookies = {"token": "good"}

        dto = await AuthService.get_current_user(Req(), FakeContainer())
        assert isinstance(dto, UserDTO)
        assert dto.username == "john"
        assert dto.email == "john@example.com"

    @pytest.mark.usefixtures("patch_jam")
    async def test_get_current_user_no_cookie(self):
        class FakeContainer: ...
        class Req:
            cookies = {}
        dto = await AuthService.get_current_user(Req(), FakeContainer())
        assert dto is None

    @pytest.mark.usefixtures("patch_jam")
    async def test_get_current_user_bad_token(self):
        class FakeContainer: ...
        class Req:
            cookies = {"token": "bad"}
        dto = await AuthService.get_current_user(Req(), FakeContainer())
        assert dto is None

    @pytest.mark.usefixtures("patch_jam")
    async def test_get_current_user_user_absent(self):
        class FakeUserService:
            async def get_user_by_id(self, user_id: str):
                return None

        class FakeContainer:
            def resolve(self, cls):
                return FakeUserService()

        class Req:
            cookies = {"token": "good"}

        dto = await AuthService.get_current_user(Req(), FakeContainer())
        assert dto is None
