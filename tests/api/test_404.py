import pytest
pytestmark = pytest.mark.asyncio

async def test_404_on_unknown_path(api_client):
    r = await api_client.get("/definitely-not-exists")
    assert r.status_code == 404
