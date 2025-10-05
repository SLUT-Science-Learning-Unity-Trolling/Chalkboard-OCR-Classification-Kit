### server_health_check
**Проверка работы сервера.**

```python
@get("/health/server", status_code=HTTP_200_OK)
def server_health_check() -> JSONResponse:
    """Проверка работы сервера."""
    return JSONResponse({"status": "ok"})
```
---
### db_health_check
**Проверка работы сервера и подключения к MongoDB.**

```python
@get("/health/db", status_code=HTTP_200_OK)
async def db_health_check() -> JSONResponse:
    """Проверка работы сервера и подключения к MongoDB."""
    try:
        await client.admin.command("ping")
        return JSONResponse({"status": "ok", "mongodb": "connected"})
    except ConnectionFailure as e:
        return JSONResponse(
            {"status": "error", "mongodb": f"failed: {str(e)}"}, status_code=500
        )
```
---