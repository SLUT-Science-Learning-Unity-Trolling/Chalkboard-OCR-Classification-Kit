import pytest

pytestmark = pytest.mark.asyncio


async def _get_schema_response(client):
    resp = await client.get("/schema/openapi.json")
    if resp.status_code == 200 and "json" in resp.headers.get("content-type", "").lower():
        return resp


    resp = await client.get("/openapi.json")
    if resp.status_code == 200 and "json" in resp.headers.get("content-type", "").lower():
        return resp


    resp = await client.get("/schema?format=openapi")
    if resp.status_code == 200 and "json" in resp.headers.get("content-type", "").lower():
        return resp


    resp = await client.get("/schema")
    return resp


async def test_openapi_schema_available(api_client):
    r = await _get_schema_response(api_client)
    assert r.status_code == 200

    ctype = r.headers.get("content-type", "").lower()
    body = r.text.strip()

    if "json" in ctype or body.startswith("{"):
        data = r.json()
        assert "openapi" in data, "Нет ключа 'openapi' в схеме"
        assert "paths" in data and isinstance(data["paths"], dict), "Нет секции 'paths'"
    else:

        assert "<!doctype html" in body.lower() or "<html" in body.lower(), "Ожидали HTML-страницу документации"
