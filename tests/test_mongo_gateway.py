import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.adapters.gateways.mongo import MongoGateway

pytestmark = pytest.mark.asyncio


@pytest.fixture(autouse=True)
def patch_config():
    with patch("app.adapters.gateways.mongo.config") as mock_config:
        mock_config.DATABASE_URL = "mongodb://localhost:27017"
        mock_config.DATABASE_NAME = "test_db"
        mock_config.DATABASE_USER = "user"
        mock_config.DATABASE_PASSWORD = "pass"
        yield mock_config


async def test_init_without_database_url(patch_config):
    patch_config.DATABASE_URL = ""
    with pytest.raises(ValueError):
        MongoGateway()


async def test_connect_success():
    gateway = MongoGateway()

    mock_client = AsyncMock()
    mock_client.admin.command = AsyncMock()

    with patch("app.adapters.gateways.mongo.AsyncMongoClient", return_value=mock_client):
        await gateway.connect()
        mock_client.admin.command.assert_called_once_with("ping")
        assert gateway._client == mock_client


async def test_connect_failure():
    gateway = MongoGateway()

    mock_client = AsyncMock()
    mock_client.admin.command = AsyncMock(side_effect=Exception("boom"))

    with patch("app.adapters.gateways.mongo.AsyncMongoClient", return_value=mock_client):
        with pytest.raises(ConnectionError):
            await gateway.connect()


async def test_get_database():
    gateway = MongoGateway()

    mock_client = AsyncMock()
    mock_client.__getitem__.return_value = "db_object"
    gateway._client = mock_client

    db = await gateway.get_database()
    assert db == "db_object"


async def test_get_collection():
    gateway = MongoGateway()

    mock_db = MagicMock()
    mock_db.__getitem__.return_value = "collection_object"

    with patch.object(gateway, "get_database", AsyncMock(return_value=mock_db)):
        collection = await gateway.get_collection("users")
        assert collection == "collection_object"
        mock_db.__getitem__.assert_called_once_with("users")


async def test_close():
    gateway = MongoGateway()

    mock_client = AsyncMock()
    gateway._client = mock_client

    await gateway.close()
    mock_client.close.assert_called_once()