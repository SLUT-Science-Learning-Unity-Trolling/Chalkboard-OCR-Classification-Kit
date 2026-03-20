# tests/test_user_service.py
from __future__ import annotations

import io
import types
from dataclasses import dataclass
from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest
from bson import ObjectId

import app.core.services.user_service as user_service_mod
from app.core.services.user_service import UserService

from app.core.errors.auth import (
    EmailAlreadyTakenError,
    PasswordDontMatchError,
    UsernameAlreadyTakenError,
)
from app.core.errors.user import (
    AbsentUserError,
    DeleteImageError,
    GetImagesError,
    ImageUploadError,
    UserCreationError,
)
from app.core.errors.validation import (
    ImageExtensionValidationError,
    ImageNotFoundError,
)

pytestmark = pytest.mark.asyncio


# Helpers / fakes

@dataclass
class FakeUploadFile:
    filename: str
    _content: bytes

    async def read(self) -> bytes:
        return self._content


class FakeMeta:
    def __init__(self, endpoint_url: str) -> None:
        self.endpoint_url = endpoint_url


class FakeClient:
    def __init__(self, endpoint_url: str) -> None:
        self.meta = FakeMeta(endpoint_url=endpoint_url)


class FakeStorage:
    def __init__(self, endpoint_url: str = "http://minio.local", bucket: str = "bucket-test") -> None:
        self._client = FakeClient(endpoint_url=endpoint_url)
        self._bucket = bucket
        self.put_object = Mock()
        self.delete_file = Mock()


def make_service(
    *,
    user_repo: Any | None = None,
    image_repo: Any | None = None,
    security: Any | None = None,
    validator: Any | None = None,
    image_validator : Any | None = None,
    storage: Any | None = None,
) -> UserService:
    user_repo = user_repo or types.SimpleNamespace(
        add=AsyncMock(),
        get_one=AsyncMock(),
        get_many=AsyncMock(),
        delete=AsyncMock(),
    )
    image_repo = image_repo or types.SimpleNamespace(
        add=AsyncMock(),
        get_one=AsyncMock(),
        get_many=AsyncMock(),
        delete=AsyncMock(),
    )
    security = security or types.SimpleNamespace(
        hash_password=Mock(return_value=("salt", "hash")),
        serialize_hash=Mock(return_value="serialized"),
    )
    validator = validator or types.SimpleNamespace(
        validate_password=Mock(),
        validate_username=Mock(),
        validate_email=Mock(),
        validate_image_extension=AsyncMock(return_value=True),
    )
    image_validator = image_validator or types.SimpleNamespace(
    validate_image_file=Mock()
    )
    storage = storage or FakeStorage()

    return UserService(
        user_repo=user_repo,
        image_repo=image_repo,
        security=security,
        validator=validator,
        image_validator=image_validator,
        storage=storage,
    )


# create_user

async def test_create_user_passwords_do_not_match_raises():
    service = make_service()
    with pytest.raises(PasswordDontMatchError):
        await service.create_user("u", "a@b.com", "p1", "p2")


async def test_create_user_username_taken_raises():
    user_repo = types.SimpleNamespace(
        add=AsyncMock(),
        get_one=AsyncMock(),
    )
    image_repo = types.SimpleNamespace(add=AsyncMock(), get_one=AsyncMock(), get_many=AsyncMock(), delete=AsyncMock())

    user_repo.get_one = AsyncMock(side_effect=[{"username": "john", "email": "x@y.com"}, None])

    service = make_service(user_repo=user_repo, image_repo=image_repo)

    with pytest.raises(UsernameAlreadyTakenError):
        await service.create_user("john", "new@b.com", "pass", "pass")


async def test_create_user_email_taken_raises():
    user_repo = types.SimpleNamespace(add=AsyncMock(), get_one=AsyncMock())
    image_repo = types.SimpleNamespace(add=AsyncMock(), get_one=AsyncMock(), get_many=AsyncMock(), delete=AsyncMock())

    user_repo.get_one = AsyncMock(side_effect=[None, {"username": "other", "email": "a@b.com"}])

    service = make_service(user_repo=user_repo, image_repo=image_repo)

    with pytest.raises(EmailAlreadyTakenError):
        await service.create_user("john", "A@B.COM", "pass", "pass")


async def test_create_user_success_creates_lower_email_and_returns_user(monkeypatch):
    user_repo = types.SimpleNamespace(add=AsyncMock(), get_one=AsyncMock())
    image_repo = types.SimpleNamespace(add=AsyncMock(), get_one=AsyncMock(), get_many=AsyncMock(), delete=AsyncMock())

    new_id = ObjectId()
    created_user = {
        "_id": new_id,
        "username": "john",
        "email": "a@b.com",
        "password_hash": "serialized",
    }
    user_repo.get_one = AsyncMock(side_effect=[None, None, created_user])
    user_repo.add = AsyncMock(return_value=new_id)

    security = types.SimpleNamespace(
        hash_password=Mock(return_value=("saltX", "hashX")),
        serialize_hash=Mock(return_value="serialized"),
    )
    validator = types.SimpleNamespace(
        validate_password=Mock(),
        validate_username=Mock(),
        validate_email=Mock(),
        validate_image_extension=AsyncMock(return_value=True),
    )

    service = make_service(user_repo=user_repo, image_repo=image_repo, security=security, validator=validator)

    user = await service.create_user("john", "A@B.COM", "pass", "pass")

    # repo.add called with lowercased email
    user_repo.add.assert_awaited_once()
    args, kwargs = user_repo.add.await_args
    assert args[0]["email"] == "a@b.com"
    assert args[0]["username"] == "john"
    assert args[0]["password_hash"] == "serialized"

    # validator calls
    validator.validate_password.assert_called_once_with("pass")
    validator.validate_username.assert_called_once_with("john")
    validator.validate_email.assert_called_once_with("A@B.COM")

    # security calls
    security.hash_password.assert_called_once_with("pass")
    security.serialize_hash.assert_called_once_with("saltX", "hashX")

    # returned object must have expected fields
    assert getattr(user, "username") == "john"
    assert getattr(user, "email") == "a@b.com"


async def test_create_user_repo_add_failure_raises_usercreationerror():
    user_repo = types.SimpleNamespace(add=AsyncMock(), get_one=AsyncMock())
    image_repo = types.SimpleNamespace(add=AsyncMock(), get_one=AsyncMock(), get_many=AsyncMock(), delete=AsyncMock())

    user_repo.get_one = AsyncMock(side_effect=[None, None])  # does_user_exists -> None/None
    user_repo.add = AsyncMock(side_effect=Exception("db down"))

    service = make_service(user_repo=user_repo, image_repo=image_repo)

    with pytest.raises(UserCreationError):
        await service.create_user("john", "a@b.com", "pass", "pass")


# does_user_exists

async def test_does_user_exists_checks_username_then_email_lower():
    user_repo = types.SimpleNamespace(add=AsyncMock(), get_one=AsyncMock())
    image_repo = types.SimpleNamespace(add=AsyncMock(), get_one=AsyncMock(), get_many=AsyncMock(), delete=AsyncMock())

    # username miss, email hit
    user_repo.get_one = AsyncMock(side_effect=[None, {"email": "x@y.com"}])

    service = make_service(user_repo=user_repo, image_repo=image_repo)

    u = await service.does_user_exists("john", "X@Y.COM")
    assert u == {"email": "x@y.com"}

    # called twice with exact queries
    calls = user_repo.get_one.await_args_list
    assert calls[0].args[0] == {"username": "john"}
    assert calls[1].args[0] == {"email": "x@y.com"}


# upload_image

async def test_upload_image_invalid_extension_raises():
    validator = types.SimpleNamespace(
        validate_password=Mock(),
        validate_username=Mock(),
        validate_email=Mock(),
        validate_image_extension=AsyncMock(return_value=False),
    )
    image_validator = types.SimpleNamespace(
    validate_image_file=Mock(side_effect=ImageExtensionValidationError("bad ext"))
    )

    service = make_service(image_validator=image_validator)

    f = FakeUploadFile(filename="bad.exe", _content=b"123")
    with pytest.raises(ImageExtensionValidationError):
        await service.upload_image(str(ObjectId()), f)


async def test_upload_image_storage_put_failure_raises():
    storage = FakeStorage()
    storage.put_object.side_effect = Exception("minio down")

    service = make_service(storage=storage)

    f = FakeUploadFile(filename="a.png", _content=b"PNGDATA")
    with pytest.raises(ImageUploadError):
        await service.upload_image(str(ObjectId()), f)


async def test_upload_image_repo_failure_raises(monkeypatch):
    storage = FakeStorage()
    image_repo = types.SimpleNamespace(add=AsyncMock(), get_one=AsyncMock(), get_many=AsyncMock(), delete=AsyncMock())
    image_repo.add = AsyncMock(side_effect=Exception("db down"))

    service = make_service(image_repo=image_repo, storage=storage)

    monkeypatch.setattr(user_service_mod, "uuid4", lambda: "UUID-123")
    monkeypatch.setattr(user_service_mod, "time", lambda: 111)

    f = FakeUploadFile(filename="a.png", _content=b"PNGDATA")
    with pytest.raises(ImageUploadError):
        await service.upload_image(str(ObjectId()), f)


async def test_upload_image_success_returns_uploaded_image(monkeypatch):
    storage = FakeStorage(endpoint_url="http://minio.local/", bucket="bucket-test")

    image_repo = types.SimpleNamespace(add=AsyncMock(), get_one=AsyncMock(), get_many=AsyncMock(), delete=AsyncMock())
    new_img_id = ObjectId()
    user_id = ObjectId()

    monkeypatch.setattr(user_service_mod, "uuid4", lambda: "UUID-123")
    monkeypatch.setattr(user_service_mod, "time", lambda: 222)

    expected_object_name = "UUID-123_a.png"
    expected_url = f"http://minio.local/bucket-test/{expected_object_name}"

    image_doc = {
        "_id": new_img_id,
        "_user_id": user_id,
        "url": expected_url,
        "uploaded_at": 222,
    }

    image_repo.add = AsyncMock(return_value=new_img_id)
    image_repo.get_one = AsyncMock(return_value=image_doc)

    service = make_service(image_repo=image_repo, storage=storage)

    f = FakeUploadFile(filename="a.png", _content=b"PNGDATA")
    uploaded = await service.upload_image(str(user_id), f)

    # storage called
    storage.put_object.assert_called_once()
    kwargs = storage.put_object.call_args.kwargs
    assert kwargs["object_name"] == expected_object_name
    assert isinstance(kwargs["data"], io.BytesIO)
    assert kwargs["size"] == len(b"PNGDATA")

    # repo called
    image_repo.add.assert_awaited_once()
    add_payload = image_repo.add.await_args.args[0]
    assert add_payload["_user_id"] == user_id
    assert add_payload["url"] == expected_url
    assert add_payload["uploaded_at"] == 222

    assert getattr(uploaded, "url") == expected_url


# get_all_user_images

async def test_get_all_user_images_success_returns_list():
    image_repo = types.SimpleNamespace(add=AsyncMock(), get_one=AsyncMock(), get_many=AsyncMock(), delete=AsyncMock())
    user_id = ObjectId()

    image_repo.get_many = AsyncMock(
        return_value=[
            {"_id": ObjectId(), "_user_id": user_id, "url": "u1", "uploaded_at": 1},
            {"_id": ObjectId(), "_user_id": user_id, "url": "u2", "uploaded_at": 2},
        ]
    )

    service = make_service(image_repo=image_repo)

    imgs = await service.get_all_user_images(str(user_id))
    assert isinstance(imgs, list)
    assert len(imgs) == 2
    assert getattr(imgs[0], "url") == "u1"
    assert getattr(imgs[1], "url") == "u2"


async def test_get_all_user_images_repo_raises_getimageserror_bubbles_as_getimageserror():
    image_repo = types.SimpleNamespace(add=AsyncMock(), get_one=AsyncMock(), get_many=AsyncMock(), delete=AsyncMock())
    image_repo.get_many = AsyncMock(side_effect=GetImagesError("boom"))

    service = make_service(image_repo=image_repo)

    with pytest.raises(GetImagesError):
        await service.get_all_user_images(str(ObjectId()))


# delete_image

async def test_delete_image_absent_user_raises():
    user_repo = types.SimpleNamespace(add=AsyncMock(), get_one=AsyncMock(), get_many=AsyncMock(), delete=AsyncMock())
    image_repo = types.SimpleNamespace(add=AsyncMock(), get_one=AsyncMock(), get_many=AsyncMock(), delete=AsyncMock())

    user_repo.get_one = AsyncMock(return_value=None)

    service = make_service(user_repo=user_repo, image_repo=image_repo)

    with pytest.raises(AbsentUserError):
        await service.delete_image("http://x/b/u.png", str(ObjectId()))


async def test_delete_image_image_not_found_raises():
    user_id = ObjectId()
    user_repo = types.SimpleNamespace(add=AsyncMock(), get_one=AsyncMock(), get_many=AsyncMock(), delete=AsyncMock())
    image_repo = types.SimpleNamespace(add=AsyncMock(), get_one=AsyncMock(), get_many=AsyncMock(), delete=AsyncMock())

    user_repo.get_one = AsyncMock(return_value={"_id": user_id})
    image_repo.get_one = AsyncMock(return_value=None)

    service = make_service(user_repo=user_repo, image_repo=image_repo)

    with pytest.raises(ImageNotFoundError):
        await service.delete_image("http://x/b/u.png", str(user_id))


async def test_delete_image_other_users_image_raises():
    user_id = ObjectId()
    other_id = ObjectId()

    user_repo = types.SimpleNamespace(add=AsyncMock(), get_one=AsyncMock(), get_many=AsyncMock(), delete=AsyncMock())
    image_repo = types.SimpleNamespace(add=AsyncMock(), get_one=AsyncMock(), get_many=AsyncMock(), delete=AsyncMock())

    user_repo.get_one = AsyncMock(return_value={"_id": user_id})
    image_repo.get_one = AsyncMock(return_value={"_user_id": other_id, "url": "http://x/b/u.png"})

    service = make_service(user_repo=user_repo, image_repo=image_repo)

    with pytest.raises(DeleteImageError):
        await service.delete_image("http://x/b/u.png", str(user_id))


async def test_delete_image_repo_delete_failure_raises():
    user_id = ObjectId()
    user_repo = types.SimpleNamespace(add=AsyncMock(), get_one=AsyncMock(), get_many=AsyncMock(), delete=AsyncMock())
    image_repo = types.SimpleNamespace(add=AsyncMock(), get_one=AsyncMock(), get_many=AsyncMock(), delete=AsyncMock())

    user_repo.get_one = AsyncMock(return_value={"_id": user_id})
    image_repo.get_one = AsyncMock(return_value={"_user_id": user_id, "url": "http://x/b/u.png"})
    image_repo.delete = AsyncMock(side_effect=Exception("db down"))

    service = make_service(user_repo=user_repo, image_repo=image_repo)

    with pytest.raises(DeleteImageError):
        await service.delete_image("http://x/b/u.png", str(user_id))


async def test_delete_image_storage_delete_failure_raises():
    user_id = ObjectId()
    user_repo = types.SimpleNamespace(add=AsyncMock(), get_one=AsyncMock(), get_many=AsyncMock(), delete=AsyncMock())
    image_repo = types.SimpleNamespace(add=AsyncMock(), get_one=AsyncMock(), get_many=AsyncMock(), delete=AsyncMock())

    user_repo.get_one = AsyncMock(return_value={"_id": user_id})
    image_repo.get_one = AsyncMock(return_value={"_user_id": user_id, "url": "http://x/b/u.png"})
    image_repo.delete = AsyncMock(return_value=None)

    storage = FakeStorage()
    storage.delete_file.side_effect = Exception("minio down")

    service = make_service(user_repo=user_repo, image_repo=image_repo, storage=storage)

    with pytest.raises(DeleteImageError):
        await service.delete_image("http://x/b/u.png", str(user_id))


async def test_delete_image_success_deletes_repo_and_storage():
    user_id = ObjectId()
    user_repo = types.SimpleNamespace(add=AsyncMock(), get_one=AsyncMock(), get_many=AsyncMock(), delete=AsyncMock())
    image_repo = types.SimpleNamespace(add=AsyncMock(), get_one=AsyncMock(), get_many=AsyncMock(), delete=AsyncMock())

    user_repo.get_one = AsyncMock(return_value={"_id": user_id})
    image_repo.get_one = AsyncMock(return_value={"_user_id": user_id, "url": "http://minio/bucket/file.png"})
    image_repo.delete = AsyncMock(return_value=None)

    storage = FakeStorage()
    service = make_service(user_repo=user_repo, image_repo=image_repo, storage=storage)

    await service.delete_image("http://minio/bucket/file.png", str(user_id))

    image_repo.delete.assert_awaited_once_with({"url": "http://minio/bucket/file.png"})
    storage.delete_file.assert_called_once_with("file.png")