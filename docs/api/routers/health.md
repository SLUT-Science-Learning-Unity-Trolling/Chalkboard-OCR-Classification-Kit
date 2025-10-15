# Модуль health

Модуль содержит эндпоинты для проверки работы сервера и подключения к MongoDB.

## def server_health_check:
#### Проверка работы сервера.
#### Маршруты:
- `@get("/health/server", status_code=HTTP_200_OK)`

#### Возвращает
| Тип | Описание |
|-----|----------|
| `JSONResponse` | Ответ |

```python
@get("/health/server", status_code=HTTP_200_OK)
def server_health_check() -> JSONResponse:
    """Проверка работы сервера.

    Returns:
        JSONResponse: Ответ
    """
    return JSONResponse({"status": "ok"})
```
---
## def db_health_check:
#### Проверка работы сервера и подключения к MongoDB.
#### Маршруты:
- `@get("/health/db", status_code=HTTP_200_OK)`

#### Возвращает
| Тип | Описание |
|-----|----------|
| `JSONResponse` | Ответ |

```python
@get("/health/db", status_code=HTTP_200_OK)
async def db_health_check() -> JSONResponse:
    """Проверка работы сервера и подключения к MongoDB.

    Returns:
        JSONResponse: Ответ
    """
    try:
        await client.admin.command("ping")
        return JSONResponse({"status": "ok", "mongodb": "connected"})
    except ConnectionFailure as e:
        return JSONResponse(
            {"status": "error", "mongodb": f"failed: {str(e)}"}, status_code=500
        )
```
---
## def minio_health_check:
#### Проверка работы сервера и подключения к MinIO.
#### Маршруты:
- `@get("/health/minio", status_code=HTTP_200_OK)`

#### Возвращает
| Тип | Описание |
|-----|----------|
| `JSONResponse` | Ответ |

```python
@get("/health/minio", status_code=HTTP_200_OK)
async def minio_health_check() -> JSONResponse:
    """Проверка работы сервера и подключения к MinIO.

    Returns:
        JSONResponse: Ответ
    """
    try:
        minio_gateway.connect()
        _ = minio_gateway._client.list_buckets()
        return JSONResponse({"status": "ok", "minio": "connected"})
    except Exception as e:
        return JSONResponse(
            {"status": "error", "minio": f"failed: {str(e)}"}, status_code=500
        )
```
---