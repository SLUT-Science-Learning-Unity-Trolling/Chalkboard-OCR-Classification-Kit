import sys
import types
import pytest
from unittest.mock import Mock, AsyncMock, patch

pytestmark = pytest.mark.asyncio

def _install_fake_config():
    fake_config_module = types.ModuleType("app.config")

    class FakeConfig:
        REDIS_HOST = "localhost"
        REDIS_PORT = 6379
        REDIS_PASSWORD = "password"

    fake_config_module.config = FakeConfig()
    sys.modules["app.config"] = fake_config_module

_install_fake_config()

from app.adapters.gateways.redis import RedisGateway


# Тесты RedisGateway
async def test_connect_success():
    gateway = RedisGateway(db=0)

    mock_client = Mock()
    mock_client.ping = Mock(return_value=True)

    with patch("app.adapters.gateways.redis.redis.Redis", return_value=mock_client):
        await gateway.connect()

        mock_client.ping.assert_called_once()
        assert gateway._client == mock_client


async def test_connect_ping_false():
    gateway = RedisGateway(db=0)

    mock_client = Mock()
    mock_client.ping = Mock(return_value=False)

    with patch("app.adapters.gateways.redis.redis.Redis", return_value=mock_client):
        with pytest.raises(ConnectionError, match="Redis did not respond to PING"):
            await gateway.connect()


async def test_connect_exception():
    gateway = RedisGateway(db=0)

    mock_client = Mock()
    mock_client.ping = Mock(side_effect=Exception("boom"))

    with patch("app.adapters.gateways.redis.redis.Redis", return_value=mock_client):
        with pytest.raises(ConnectionError, match="Failed to connect to Redis: boom"):
            await gateway.connect()


async def test_get_connection_calls_connect():
    gateway = RedisGateway(db=0)

    with patch.object(gateway, "connect", AsyncMock()) as mock_connect:
        gateway._client = AsyncMock()
        conn = await gateway.get_connection()

        mock_connect.assert_not_called() 
        assert conn is gateway._client

    gateway2 = RedisGateway(db=1)
    gateway2._client = None
    with patch.object(gateway2, "connect", AsyncMock()) as mock_connect2:
        conn2 = await gateway2.get_connection()
        mock_connect2.assert_awaited_once()


async def test_close():
    gateway = RedisGateway(db=0)

    mock_client = AsyncMock()
    gateway._client = mock_client

    await gateway.close()

    mock_client.close.assert_awaited_once()
    assert gateway._client is None