import sys
import types
import importlib.util
from pathlib import Path
from dataclasses import dataclass
from typing import Any

import pytest
from bson import ObjectId


def _load_users_module():
    project_root = Path(__file__).resolve().parents[1]
    user_py = project_root / "app" / "api" / "routers" / "user.py"
    assert user_py.exists(), f"Не найден файл: {user_py}"

    module_name = "test_loaded_users_router_module"
    spec = importlib.util.spec_from_file_location(module_name, str(user_py))
    assert spec and spec.loader

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


users_module = _load_users_module()


@dataclass
class FakeUserCreateDTO:
    username: str
    email: str
    password: str
    repeat_password: str


@dataclass
class FakeUserDTO:
    id: str
    username: str
    email: str

    @classmethod
    def fromrow(cls, row: dict[str, Any]) -> "FakeUserDTO":
        return cls(
            id=str(row.get("id") or row.get("_id") or ""),
            username=row["username"],
            email=row["email"],
        )


@dataclass
class FakeImageDTO:
    id: str
    url: str

    @classmethod
    def fromrow(cls, row: dict[str, Any]) -> "FakeImageDTO":
        _id = row.get("_id") or row.get("id") or ""
        return cls(id=str(_id), url=row["url"])


class FakeUploadedImage:
    def __init__(self, _id: Any, url: str) -> None:
        self._id = _id
        self.url = url


class FakeUser:
    def __init__(self, id: str, username: str, email: str) -> None:
        self.id = id
        self.username = username
        self.email = email


class FakeUploadFile:
    def __init__(self, filename: str = "x.png") -> None:
        self.filename = filename


@dataclass
class FakeCurrentUserDTO:
    id: str


class FakeUserService:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[Any, ...], dict[str, Any]]] = []

    async def create_user(self, username: str, email: str, password: str, repeat_password: str) -> FakeUser:
        self.calls.append(("create_user", (username, email, password, repeat_password), {}))
        return FakeUser(id="u1", username=username, email=email)

    async def upload_image(self, user_id: str, file: Any) -> FakeUploadedImage:
        self.calls.append(("upload_image", (user_id, file), {}))
        return FakeUploadedImage(_id=ObjectId("65f000000000000000000001"), url="https://cdn/img1.png")

    async def get_all_user_images(self, user_id: str):
        self.calls.append(("get_all_user_images", (user_id,), {}))
        return [
            FakeUploadedImage(_id=ObjectId("65f000000000000000000002"), url="https://cdn/a.png"),
            FakeUploadedImage(_id=ObjectId("65f000000000000000000003"), url="https://cdn/b.png"),
        ]

    async def delete_image(self, user_id: str, url: str) -> None:
        self.calls.append(("delete_image", (user_id, url), {}))
        return None


class FakeContainer:
    def __init__(self, service: Any) -> None:
        self._service = service

    def resolve(self, cls: Any) -> Any:
        return self._service


def _handler_fn(route_handler_obj):
    """
    Litestar декораторы @post/@get/@delete превращают функцию в HTTPRouteHandler.
    Оригинальная функция лежит в .fn
    """
    fn = getattr(route_handler_obj, "fn", None)
    assert fn is not None, "Не смог достать оригинальную функцию из route handler (нет .fn)"
    return fn


@pytest.fixture(autouse=True)
def patch_dtos(monkeypatch):
    monkeypatch.setattr(users_module, "UserDTO", FakeUserDTO, raising=True)
    monkeypatch.setattr(users_module, "ImageDTO", FakeImageDTO, raising=True)
    yield


@pytest.mark.asyncio
async def test_create_user_calls_service_and_returns_dict():
    service = FakeUserService()
    container = FakeContainer(service)

    fn = _handler_fn(users_module.create_user)

    data = FakeUserCreateDTO(
        username="john",
        email="john@example.com",
        password="12345678",
        repeat_password="12345678",
    )

    result = await fn(data=data, container=container)

    assert isinstance(result, dict)
    assert result["username"] == "john"
    assert result["email"] == "john@example.com"
    assert "id" in result

    assert service.calls[0][0] == "create_user"
    assert service.calls[0][1] == ("john", "john@example.com", "12345678", "12345678")


@pytest.mark.asyncio
async def test_upload_image_converts_objectid_to_str_and_returns_imagedto():
    service = FakeUserService()
    container = FakeContainer(service)

    fn = _handler_fn(users_module.upload_image)

    current_user = FakeCurrentUserDTO(id="u1")
    upload = FakeUploadFile("pic.png")

    image_dto = await fn(container=container, current_user=current_user, data=upload)

    assert isinstance(image_dto, FakeImageDTO)
    assert image_dto.url == "https://cdn/img1.png"
    assert isinstance(image_dto.id, str)
    assert image_dto.id == "65f000000000000000000001"

    assert service.calls[0][0] == "upload_image"
    assert service.calls[0][1][0] == "u1" 
    assert service.calls[0][1][1] is upload 


@pytest.mark.asyncio
async def test_get_all_user_images_returns_list_of_imagedto():
    service = FakeUserService()
    container = FakeContainer(service)

    fn = _handler_fn(users_module.get_all_user_images)

    current_user = FakeCurrentUserDTO(id="u1")

    result = await fn(container=container, current_user=current_user)

    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(x, FakeImageDTO) for x in result)

    assert result[0].url == "https://cdn/a.png"
    assert result[0].id == "65f000000000000000000002"
    assert result[1].url == "https://cdn/b.png"
    assert result[1].id == "65f000000000000000000003"

    assert service.calls[0][0] == "get_all_user_images"
    assert service.calls[0][1] == ("u1",)


@pytest.mark.asyncio
async def test_delete_image_calls_service_and_returns_detail():
    service = FakeUserService()
    container = FakeContainer(service)

    fn = _handler_fn(users_module.delete_image)

    current_user = FakeCurrentUserDTO(id="u1")

    result = await fn(container=container, current_user=current_user, url="https://cdn/a.png")

    assert result == {"detail": "Изображение удалено"}

    assert service.calls[0][0] == "delete_image"
    assert service.calls[0][1] == ("u1", "https://cdn/a.png")