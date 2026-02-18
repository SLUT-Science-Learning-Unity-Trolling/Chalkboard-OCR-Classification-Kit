from __future__ import annotations

import importlib
import types
import pytest
from httpx import AsyncClient, ASGITransport


@pytest.fixture(scope="session", autouse=True)
def _patch_external_gateways_before_import():
    """
    Подготавливает окружение для тестов:
    - Подменяет S3/Boto3 клиента на фейковый, чтобы не обращаться к Minio.
    - Глушит MongoGateway (если он есть в проекте).
    """
    mp = pytest.MonkeyPatch()

    # ---------------------- S3 / Minio ----------------------
    class _FakeS3Client:
        def list_buckets(self):
            # MinioGateway.connect вызывает этот метод
            return {"Buckets": []}

        def head_bucket(self, Bucket):
            return {}

        def create_bucket(self, Bucket):
            return {}

        @property
        def meta(self):
            return types.SimpleNamespace(endpoint_url="http://minio.test")

    # Подменяем символ client, импортируемый в app.adapters.gateways.s3
    mp.setattr(
        "app.adapters.gateways.s3.client",
        lambda *args, **kwargs: _FakeS3Client(),
        raising=False,
    )

    # ---------------------- Mongo (если используется) ----------------------
    try:
        import app.adapters.gateways.mongo as mongomod

        class _DummyCollection:
            async def find_one(self, *_a, **_kw):
                return None

            async def insert_one(self, *_a, **_kw):
                class _R:
                    inserted_id = "dummy-id"
                return _R()

            async def update_one(self, *_a, **_kw):
                class _R:
                    matched_count = 0
                return _R()

            async def delete_one(self, *_a, **_kw):
                class _R:
                    deleted_count = 0
                return _R()

        class _DummyDB:
            def __getitem__(self, _name: str):
                return _DummyCollection()

        async def _noop_connect(self):
            return None

        async def _fake_get_database(self):
            return _DummyDB()

        async def _fake_get_collection(self, _name: str):
            return _DummyCollection()

        mp.setattr(mongomod.MongoGateway, "connect", _noop_connect, raising=True)
        mp.setattr(mongomod.MongoGateway, "get_database", _fake_get_database, raising=True)
        mp.setattr(mongomod.MongoGateway, "get_collection", _fake_get_collection, raising=True)
    except Exception:
        # Если модуль Mongo отсутствует, просто игнорируем
        pass

    # ---------------------- yield/cleanup ----------------------
    yield
    mp.undo()


@pytest.fixture(scope="session")
def fastapi_app(_patch_external_gateways_before_import):
    """
    Импортирует приложение после всех патчей, чтобы при импорте
    роутеров не создавался реальный MinioClient и не шёл запрос к сети.
    """
    app_mod = importlib.import_module("app.main")
    return app_mod.app


@pytest.fixture
async def api_client(fastapi_app):
    """
    Асинхронный HTTP-клиент для интеграционных тестов.
    """
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
