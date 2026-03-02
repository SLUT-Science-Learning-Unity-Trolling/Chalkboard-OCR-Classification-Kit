import sys
import importlib.util
from pathlib import Path

import pytest
from punq import Container
from litestar import Litestar
from litestar.di import Provide
from litestar.testing import TestClient

from app.api.schemas.user_dto import UserDTO


def _load_auth_module():
    """
    Загружаем app/api/routers/auth.py напрямую по пути к файлу,
    чтобы НЕ выполнялся app/api/routers/__init__.py и не импортировались
    другие роутеры (health.py), которые тянут boto3/minio и ломают collection.

    Также регистрируем модуль в sys.modules, потому что Litestar
    резолвит type hints через sys.modules[fn.__module__].
    """
    project_root = Path(__file__).resolve().parents[1]
    auth_path = project_root / "app" / "api" / "routers" / "auth.py"

    module_name = "test_loaded_auth_router_module"
    spec = importlib.util.spec_from_file_location(module_name, auth_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module spec from {auth_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


auth_module = _load_auth_module()
auth_router = auth_module.auth_router


# --- Подмена dependency для /auth/me ---
# В auth.py: get_me имеет dependencies={"current_user": Provide(AuthService.get_current_user)}
# App-level dependencies это не переопределяет, поэтому патчим прямо handler.
async def _provide_current_user() -> UserDTO:
    return UserDTO(
        id="694de2b36e5be2ab74f350e6",
        username="User123",
        email="user@example.com",
    )


# get_me в модуле — это уже RouteHandler (результат декоратора @get), у него есть .dependencies
auth_module.get_me.dependencies["current_user"] = Provide(_provide_current_user)


class FakeAuthService:
    """Фейковый AuthService для тестов роутеров auth.py."""

    def __init__(self) -> None:
        self.blacklisted: list[tuple[str, str, int]] = []

    async def auth_existing_user(self, identifier: str, password: str, client_ip: str):
        # auth.py делает: user_dto = UserDTO.fromrow(user.__dict__)
        # Значит у "user" должен быть __dict__ с нужными полями.
        class UserObj:
            def __init__(self):
                self.id = "694de2b36e5be2ab74f350e6"
                self.username = "User123"
                self.email = "user@example.com"

        user = UserObj()
        access_token = "access.token.value"
        refresh_token = "refresh.token.value"
        return user, access_token, refresh_token

    async def refresh_tokens(self, refresh_token: str | None, access_token: str | None, client_ip: str):
        return "new.access.token", "new.refresh.token"

    async def _blacklist_token(self, token: str, expected_type: str, expires_in: int):
        self.blacklisted.append((token, expected_type, expires_in))


@pytest.fixture()
def fake_auth_service() -> FakeAuthService:
    return FakeAuthService()


@pytest.fixture()
def client(fake_auth_service: FakeAuthService) -> TestClient:
    container = Container()

    # Регистрируем реальный класс AuthService -> инстанс нашего фейка
    from app.core.services.auth_service import AuthService
    container.register(AuthService, instance=fake_auth_service)

    def provide_container() -> Container:
        return container

    app = Litestar(
        route_handlers=[auth_router],
        dependencies={
            "container": Provide(provide_container, sync_to_thread=False),
        },
    )
    return TestClient(app)


def test_login_success_sets_cookies_and_returns_user(client: TestClient):
    resp = client.post(
        "/auth/login",
        json={"identifier": "user@example.com", "password": "12345678"},
        headers={"X-Forwarded-For": "127.0.0.1"},
    )

    assert resp.status_code == 200

    data = resp.json()
    assert data["id"] == "694de2b36e5be2ab74f350e6"
    assert data["username"] == "User123"
    assert data["email"] == "user@example.com"

    set_cookie = resp.headers.get("set-cookie", "")
    assert "access_token=" in set_cookie
    assert "refresh_token=" in set_cookie


def test_logout_without_tokens_still_works(client: TestClient, fake_auth_service: FakeAuthService):
    resp = client.post("/auth/logout")

    assert resp.status_code == 200
    assert resp.json()["detail"] == "Пользователь успешно вышел из аккаунта"

    assert fake_auth_service.blacklisted == []

    set_cookie = resp.headers.get("set-cookie", "")
    assert "access_token=" in set_cookie
    assert "refresh_token=" in set_cookie


def test_logout_with_tokens_blacklists_both(client: TestClient, fake_auth_service: FakeAuthService):
    client.cookies.set("access_token", "access.token.value")
    client.cookies.set("refresh_token", "refresh.token.value")

    resp = client.post("/auth/logout")
    assert resp.status_code == 200

    assert any(t[0] == "refresh.token.value" and t[1] == "refresh" for t in fake_auth_service.blacklisted)
    assert any(t[0] == "access.token.value" and t[1] == "access" for t in fake_auth_service.blacklisted)


def test_refresh_success_sets_new_cookies(client: TestClient):
    client.cookies.set("access_token", "old.access")
    client.cookies.set("refresh_token", "old.refresh")

    resp = client.post("/auth/refresh")
    assert resp.status_code == 200
    assert resp.json()["detail"] == "Token refreshed"

    set_cookie = resp.headers.get("set-cookie", "")
    assert "access_token=" in set_cookie
    assert "refresh_token=" in set_cookie


def test_get_me_returns_current_user(client: TestClient):
    resp = client.get("/auth/me")
    assert resp.status_code == 200

    data = resp.json()
    assert data["id"] == "694de2b36e5be2ab74f350e6"
    assert data["username"] == "User123"
    assert data["email"] == "user@example.com"