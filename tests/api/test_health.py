import pytest
pytestmark = pytest.mark.asyncio

async def test_health_server_ok(api_client):
    r = await api_client.get("/health/server")
    assert r.status_code == 200
