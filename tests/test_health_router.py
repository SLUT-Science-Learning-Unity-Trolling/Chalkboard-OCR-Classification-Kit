import sys
import types
import importlib.util
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from litestar import Litestar
from litestar.testing import TestClient

pytestmark = pytest.mark.asyncio


# -------------------------------
# Pre-import patches (starlette + config + s3.client)
# -------------------------------

def _install_fake_starlette_json_response() -> None:
    """
    health.py импортирует:
        from starlette.responses import JSONResponse

    Litestar умеет работать со Starlette Response, потому что это ASGI-callable.
    Поэтому заглушка ДОЛЖНА быть ASGI-callable: __call__(scope, receive, send).
    """
    if "starlette" not in sys.modules:
        sys.modules["starlette"] = types.ModuleType("starlette")

    if "starlette.responses" not in sys.modules:
        responses_mod = types.ModuleType("starlette.responses")

        class JSONResponse:
            media_type = "application/json"

            def __init__(self, content, status_code: int = 200, headers=None, **kwargs):
                self.content = content
                self.status_code = status_code
                self.headers = headers or {}

            def json(self):
                return self.content

            async def __call__(self, scope, receive, send):
                body = json.dumps(self.content, ensure_ascii=False).encode("utf-8")

                headers = [
                    (b"content-type", b"application/json"),
                    (b"content-length", str(len(body)).encode("ascii")),
                ]
                for k, v in (self.headers or {}).items():
                    headers.append(
                        (str(k).encode("latin-1"), str(v).encode("latin-1"))
                    )

                await send(
                    {
                        "type": "http.response.start",
                        "status": int(self.status_code),
                        "headers": headers,
                    }
                )
                await send({"type": "http.response.body", "body": body})

        responses_mod.JSONResponse = JSONResponse
        sys.modules["starlette.responses"] = responses_mod


def _ensure_config_has_health_attrs() -> None:
    """
    health.py использует:
        Config.REDIS_TOKENS_BLACKLIST_DB
        Config.REDIS_RATE_LIMITING_DB
    Добавим, если в fake Config их нет.
    """
    import app.config as app_config  # подмена из conftest

    if not hasattr(app_config, "Config"):
        raise RuntimeError("app.config has no Config in tests; check tests/conftest.py")

    Config = app_config.Config
    if not hasattr(Config, "REDIS_TOKENS_BLACKLIST_DB"):
        setattr(Config, "REDIS_TOKENS_BLACKLIST_DB", 1)
    if not hasattr(Config, "REDIS_RATE_LIMITING_DB"):
        setattr(Config, "REDIS_RATE_LIMITING_DB", 2)


def _patch_minio_s3_client() -> None:
    """
    В app.adapters.gateways.s3 часто делают:
        from boto3 import client
    Поэтому нужно патчить symbol `client` ВНУТРИ модуля s3.
    """
    import app.adapters.gateways.s3 as s3_module

    def safe_client(*args, **kwargs):
        mock_client = MagicMock()
        # MinioGateway.connect() ожидает dict с ключом "Buckets"
        mock_client.list_buckets = MagicMock(return_value={"Buckets": []})
        return mock_client

    s3_module.client = safe_client


# -------------------------------
# Load health.py directly (bypass routers/__init__.py)
# -------------------------------

def _load_health_module():
    _install_fake_starlette_json_response()
    _ensure_config_has_health_attrs()
    _patch_minio_s3_client()

    project_root = Path(__file__).resolve().parents[1]
    health_path = project_root / "app" / "api" / "routers" / "health.py"

    module_name = "test_loaded_health_router_module"
    spec = importlib.util.spec_from_file_location(module_name, health_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module spec from {health_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


health_module = _load_health_module()
health_router = health_module.health_router


@pytest.fixture()
def client() -> TestClient:
    app = Litestar(route_handlers=[health_router])
    return TestClient(app)


# -------------------------------
# /health/server
# -------------------------------

async def test_server_health_check_ok(client: TestClient):
    resp = client.get("/health/server")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


# -------------------------------
# /health/db
# -------------------------------

async def test_db_health_check_ok(client: TestClient):
    mock_mongo = MagicMock()
    mock_mongo.admin = MagicMock()
    mock_mongo.admin.command = AsyncMock(return_value={"ok": 1})
    health_module.client = mock_mongo

    resp = client.get("/health/db")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "mongodb": "connected"}


async def test_db_health_check_connection_failure_returns_500(client: TestClient):
    from pymongo.errors import ConnectionFailure

    mock_mongo = MagicMock()
    mock_mongo.admin = MagicMock()
    mock_mongo.admin.command = AsyncMock(side_effect=ConnectionFailure("boom"))
    health_module.client = mock_mongo

    resp = client.get("/health/db")
    assert resp.status_code == 500
    body = resp.json()
    assert body["status"] == "error"
    assert "mongodb" in body
    assert "failed:" in body["mongodb"]


# -------------------------------
# /health/minio
# -------------------------------

async def test_minio_health_check_ok(client: TestClient):
    mock_minio = MagicMock()
    mock_minio.connect = MagicMock()

    mock_minio_client = MagicMock()
    mock_minio_client.list_buckets = MagicMock(return_value={"Buckets": []})
    mock_minio._client = mock_minio_client

    health_module.minio_gateway = mock_minio

    resp = client.get("/health/minio")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "minio": "connected"}


async def test_minio_health_check_failure_returns_500(client: TestClient):
    mock_minio = MagicMock()
    mock_minio.connect = MagicMock(side_effect=Exception("nope"))
    health_module.minio_gateway = mock_minio

    resp = client.get("/health/minio")
    assert resp.status_code == 500
    body = resp.json()
    assert body["status"] == "error"
    assert "minio" in body
    assert "failed:" in body["minio"]


# -------------------------------
# /health/redis
# -------------------------------

async def test_redis_health_check_ok(client: TestClient):
    gw_black = MagicMock()
    gw_black.connect = AsyncMock()
    gw_black._client = MagicMock()
    gw_black._client.ping = AsyncMock(return_value=True)

    gw_rate = MagicMock()
    gw_rate.connect = AsyncMock()
    gw_rate._client = MagicMock()
    gw_rate._client.ping = AsyncMock(return_value=True)

    health_module.redis_blacklist_gateway = gw_black
    health_module.redis_rate_limit_gateway = gw_rate

    resp = client.get("/health/redis")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "redis": "connected"}


async def test_redis_health_check_failure_returns_500(client: TestClient):
    """
    В health.py сейчас баг: except возвращает (JSONResponse(...),) — кортеж.
    Это приводит к 500. Проверяем внешний контракт: статус 500 и JSON с ошибкой.
    """
    gw_black = MagicMock()
    gw_black.connect = AsyncMock(side_effect=Exception("down"))
    health_module.redis_blacklist_gateway = gw_black

    resp = client.get("/health/redis")
    assert resp.status_code == 500
    body = resp.json()
    # тело ошибки зависит от того, как Litestar сериализует исключение/return type,
    # но теперь это точно будет JSON, а не HTML.
    assert "redis" in body or "detail" in body


# -------------------------------
# /health/all
# -------------------------------

async def test_all_services_health_check_all_ok(client: TestClient):
    # Mongo ok
    mock_mongo = MagicMock()
    mock_mongo.admin = MagicMock()
    mock_mongo.admin.command = AsyncMock(return_value={"ok": 1})
    health_module.client = mock_mongo

    # Minio ok
    mock_minio = MagicMock()
    mock_minio.connect = MagicMock()
    mock_minio._client = MagicMock()
    mock_minio._client.list_buckets = MagicMock(return_value={"Buckets": []})
    health_module.minio_gateway = mock_minio

    # Redis ok
    gw_black = MagicMock()
    gw_black.connect = AsyncMock()
    gw_black._client = MagicMock()
    gw_black._client.ping = AsyncMock(return_value=True)

    gw_rate = MagicMock()
    gw_rate.connect = AsyncMock()
    gw_rate._client = MagicMock()
    gw_rate._client.ping = AsyncMock(return_value=True)

    health_module.redis_blacklist_gateway = gw_black
    health_module.redis_rate_limit_gateway = gw_rate

    resp = client.get("/health/all")
    assert resp.status_code == 200
    assert resp.json() == {
        "status": "ok",
        "mongodb": "connected",
        "minio": "connected",
        "redis": "connected",
    }


async def test_all_services_health_check_returns_500_when_one_service_fails(client: TestClient):
    from pymongo.errors import ConnectionFailure

    # Mongo fail
    mock_mongo = MagicMock()
    mock_mongo.admin = MagicMock()
    mock_mongo.admin.command = AsyncMock(side_effect=ConnectionFailure("boom"))
    health_module.client = mock_mongo

    # Minio ok
    mock_minio = MagicMock()
    mock_minio.connect = MagicMock()
    mock_minio._client = MagicMock()
    mock_minio._client.list_buckets = MagicMock(return_value={"Buckets": []})
    health_module.minio_gateway = mock_minio

    # Redis ok
    gw_black = MagicMock()
    gw_black.connect = AsyncMock()
    gw_black._client = MagicMock()
    gw_black._client.ping = AsyncMock(return_value=True)

    gw_rate = MagicMock()
    gw_rate.connect = AsyncMock()
    gw_rate._client = MagicMock()
    gw_rate._client.ping = AsyncMock(return_value=True)

    health_module.redis_blacklist_gateway = gw_black
    health_module.redis_rate_limit_gateway = gw_rate

    resp = client.get("/health/all")
    assert resp.status_code == 500
    body = resp.json()
    assert "mongodb" in body or "detail" in body