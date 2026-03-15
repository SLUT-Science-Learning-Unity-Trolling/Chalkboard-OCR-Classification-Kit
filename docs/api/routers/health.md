# Модуль health

Модуль содержит эндпоинты для проверки работы сервера и подключения к сервисам.

## def server_health_check:
#### Проверка работы сервера.
#### Маршрут:
- **Декоратор:** @get
- **Маршрут:** `/server`
- **Заголовок:** Проверка работы сервера
- **Описание:** Эндпоинт проверяет доступность сервера
- **Теги:** Debug


```python
@get(
    "/server",
    summary="Проверка работы сервера",
    description="Эндпоинт проверяет доступность сервера",
    tags=["Debug"],
    status_code=HTTP_200_OK,
    responses={
        HTTP_200_OK: ResponseSpec(
            description="Сервер работает",
            data_container=None,
            examples=[
                Example(
                    value={"status": "ok"},
                )
            ],
        ),
        HTTP_500_INTERNAL_SERVER_ERROR: ResponseSpec(
            description="Сервер недоступен",
            data_container=ErrorMeta,
            examples=[
                Example(
                    value=problem_factory.build(
                        error=ErrorCode.SERVICE_CONNECTION_ERROR,
                        detail="Сервер не отвечает",
                    ),
                )
            ],
        ),
    },
)
def server_health_check() -> JSONResponse:
    """Проверка работы сервера."""
    return JSONResponse({"status": "ok"})
```
---
## def db_health_check:
#### Проверка подключения к MongoDB.
#### Маршрут:
- **Декоратор:** @get
- **Маршрут:** `/db`
- **Заголовок:** Проверка подключения к MongoDB
- **Описание:** Эндпоинт проверяет возможность подключения к MongoDB
- **Теги:** Debug


```python
@get(
    "/db",
    summary="Проверка подключения к MongoDB",
    description="Эндпоинт проверяет возможность подключения к MongoDB",
    tags=["Debug"],
    status_code=HTTP_200_OK,
    responses={
        HTTP_200_OK: ResponseSpec(
            description="MongoDB подключена",
            data_container=None,
            examples=[
                Example(
                    value={"status": "ok", "mongodb": "connected"},
                )
            ],
        ),
        HTTP_500_INTERNAL_SERVER_ERROR: ResponseSpec(
            description="Ошибка подключения к MongoDB",
            data_container=ErrorMeta,
            examples=[
                Example(
                    value=problem_factory.build(
                        error=ErrorCode.SERVICE_CONNECTION_ERROR,
                        detail="Не удалось подключиться к MongoDB",
                    ),
                )
            ],
        ),
    },
)
async def db_health_check() -> JSONResponse:
    """Проверка подключения к MongoDB."""
    try:
        await client.admin.command("ping")
        return JSONResponse({"status": "ok", "mongodb": "connected"})
    except ConnectionFailure as e:
        return JSONResponse(
            {"status": "error", "mongodb": f"failed: {str(e)}"},
            status_code=500,
        )
```
---
## def minio_health_check:
#### Проверка подключения к MinIO.
#### Маршрут:
- **Декоратор:** @get
- **Маршрут:** `/minio`
- **Заголовок:** Проверка подключения к MinIO
- **Описание:** Эндпоинт проверяет возможность подключения к MinIO
- **Теги:** Debug


```python
@get(
    "/minio",
    summary="Проверка подключения к MinIO",
    description="Эндпоинт проверяет возможность подключения к MinIO",
    tags=["Debug"],
    status_code=HTTP_200_OK,
    responses={
        HTTP_200_OK: ResponseSpec(
            description="MinIO подключен",
            data_container=None,
            examples=[
                Example(
                    value={"status": "ok", "minio": "connected"},
                )
            ],
        ),
        HTTP_500_INTERNAL_SERVER_ERROR: ResponseSpec(
            description="Ошибка подключения к MinIO",
            data_container=ErrorMeta,
            examples=[
                Example(
                    value=problem_factory.build(
                        error=ErrorCode.SERVICE_CONNECTION_ERROR,
                        detail="Не удалось подключиться к MinIO",
                    ),
                )
            ],
        ),
    },
)
async def minio_health_check() -> JSONResponse:
    """Проверка подключения к MinIO."""
    try:
        minio_gateway.connect()
        _ = minio_gateway._client.list_buckets()
        return JSONResponse({"status": "ok", "minio": "connected"})
    except Exception as e:
        return JSONResponse(
            {"status": "error", "minio": f"failed: {str(e)}"},
            status_code=500,
        )
```
---
## def redis_health_check:
#### Проверка подключения к Redis.
#### Маршрут:
- **Декоратор:** @get
- **Маршрут:** `/redis`
- **Заголовок:** Проверка подключения к Redis
- **Описание:** Эндпоинт проверяет возможность подключения к Redis
- **Теги:** Debug


```python
@get(
    "/redis",
    summary="Проверка подключения к Redis",
    description="Эндпоинт проверяет возможность подключения к Redis",
    tags=["Debug"],
    status_code=HTTP_200_OK,
    responses={
        HTTP_200_OK: ResponseSpec(
            description="Redis подключен",
            data_container=None,
            examples=[
                Example(
                    value={"status": "ok", "redis": "connected"},
                )
            ],
        ),
        HTTP_500_INTERNAL_SERVER_ERROR: ResponseSpec(
            description="Ошибка подключения к Redis",
            data_container=ErrorMeta,
            examples=[
                Example(
                    value=problem_factory.build(
                        error=ErrorCode.SERVICE_CONNECTION_ERROR,
                        detail="Не удалось подключиться к Redis",
                    ),
                )
            ],
        ),
    },
)
async def redis_health_check() -> JSONResponse:
    """Проверка подключения к Redis."""
    try:
        await redis_blacklist_gateway.connect()
        _: Redis = await redis_blacklist_gateway._client.ping()
        await redis_rate_limit_gateway.connect()
        _: Redis = await redis_rate_limit_gateway._client.ping()
        return JSONResponse({"status": "ok", "redis": "connected"})
    except Exception as e:
        return (
            JSONResponse(
                {"status": "error", "redis": f"failed: {str(e)}"},
                status_code=500,
            ),
        )
```
---
## def all_services_health_check:
#### Проверка подключения ко всем сервисам.
#### Маршрут:
- **Декоратор:** @get
- **Маршрут:** `/all`
- **Заголовок:** Проверка подключения ко всем сервисам
- **Описание:** Эндпоинт проверяет возможность подключения ко всем сервисам (MongoDB, MinIO, Redis)
- **Теги:** Debug


```python
@get(
    "/all",
    summary="Проверка подключения ко всем сервисам",
    description="Эндпоинт проверяет возможность подключения ко всем сервисам (MongoDB, MinIO, Redis)",
    tags=["Debug"],
    status_code=HTTP_200_OK,
    responses={
        HTTP_200_OK: ResponseSpec(
            description="Все сервисы подключены",
            data_container=None,
            examples=[
                Example(
                    value={
                        "status": "ok",
                        "mongodb": "connected",
                        "minio": "connected",
                        "redis": "connected",
                    },
                )
            ],
        ),
        HTTP_500_INTERNAL_SERVER_ERROR: ResponseSpec(
            description="Ошибка подключения к одному или нескольким сервисам",
            data_container=ErrorMeta,
            examples=[
                Example(
                    value=problem_factory.build(
                        error=ErrorCode.SERVICE_CONNECTION_ERROR,
                        detail="Не удалось подключиться к одному или нескольким сервисам",
                    ),
                )
            ],
        ),
    },
)
async def all_services_health_check() -> JSONResponse:
    """Проверка подключения ко всем сервисам."""
    errors = {}

    # Проверка MongoDB
    try:
        await client.admin.command("ping")
    except ConnectionFailure as e:
        errors["mongodb"] = f"failed: {str(e)}"

    # Проверка MinIO
    try:
        minio_gateway.connect()
        _ = minio_gateway._client.list_buckets()
    except Exception as e:
        errors["minio"] = f"failed: {str(e)}"

    # Проверка Redis
    try:
        await redis_blacklist_gateway.connect()
        _: Redis = await redis_blacklist_gateway._client.ping()
        await redis_rate_limit_gateway.connect()
        _: Redis = await redis_rate_limit_gateway._client.ping()
    except Exception as e:
        errors["redis"] = f"failed: {str(e)}"

    if not errors:
        return JSONResponse(
            {
                "status": "ok",
                "mongodb": "connected",
                "minio": "connected",
                "redis": "connected",
            }
        )
    else:
        return JSONResponse({"status": "error", **errors}, status_code=500)
```
---
## def metrics_handler:
#### Маршрут:
- **Декоратор:** @get
- **Маршрут:** `/metrics`
- **Заголовок:** Показать метрики Prometheus
- **Описание:** Эндпоинт возвращает метрики в формате Prometheus
- **Теги:** Debug


```python
@get(
    "/metrics",
    summary="Показать метрики Prometheus",
    description="Эндпоинт возвращает метрики в формате Prometheus",
    tags=["Debug"],
    status_code=HTTP_200_OK,
)
def metrics_handler() -> PlainTextResponse:
    data, ctype = metrics_endpoint()
    return PlainTextResponse(content=data, media_type=ctype)
```
---
## def metrics_json_handler:
#### Маршрут:
- **Декоратор:** @get
- **Маршрут:** `/metrics/json`
- **Заголовок:** Метрики Prometheus в JSON
- **Описание:** Возвращает метрики в удобочитаемом JSON для дебага
- **Теги:** Debug


```python
@get(
    "/metrics/json",
    summary="Метрики Prometheus в JSON",
    description="Возвращает метрики в удобочитаемом JSON для дебага",
    tags=["Debug"],
)
def metrics_json_handler() -> JSONResponse:
    data = metrics_as_json()
    return JSONResponse(content=json.loads(data))
```
---