"""Модуль содержит эндпоинты для проверки работы сервера и подключения к сервисам."""
# API_Health

from litestar import get
from litestar.status_codes import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR
from litestar.openapi import ResponseSpec
from litestar.openapi.spec import Example
from starlette.responses import JSONResponse
from pymongo import AsyncMongoClient
from pymongo.errors import ConnectionFailure

from app.adapters.gateways.redis import RedisGateway
from app.adapters.gateways.s3 import MinioGateway
from app.api.exceptions.problem_factory import ErrorCodes
from app.config import Config
from app.api.exceptions.problem_details_dto import ProblemDetailsDTO

client = AsyncMongoClient(Config.DATABASE_URL)
minio_gateway = MinioGateway()
redis_gateway = RedisGateway()

@get(
    "/health/server",
    summary="Проверка работы сервера",
    description="Эндпоинт проверяет доступность сервера",
    tags=["Дебаг"],
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
            data_container=ProblemDetailsDTO,
            examples=[
                Example(
                    value=ErrorCodes.SERVICE_CONNECTION_ERROR.example(
                        "Сервер не отвечает"
                    ),
                )
            ],
        ),
    },
)
def server_health_check() -> JSONResponse:
    """Проверка работы сервера."""
    return JSONResponse({"status": "ok"})


@get(
    "/health/db",
    summary="Проверка подключения к MongoDB",
    description="Эндпоинт проверяет возможность подключения к MongoDB",
    tags=["Дебаг"],
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
            data_container=ProblemDetailsDTO,
            examples=[
                Example(
                    value=ErrorCodes.SERVICE_CONNECTION_ERROR.example(
                        "Не удалось подключиться к MongoDB"
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


@get(
    "/health/minio",
    summary="Проверка подключения к MinIO",
    description="Эндпоинт проверяет возможность подключения к MinIO",
    tags=["Дебаг"],
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
            data_container=ProblemDetailsDTO,
            examples=[
                Example(
                    value=ErrorCodes.SERVICE_CONNECTION_ERROR.example(
                        "Не удалось подключиться к MinIO"
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

@get(
    "/health/redis",
    summary="Проверка подключения к Redis",
    description="Эндпоинт проверяет возможность подключения к Redis",
    tags=["Дебаг"],
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
            data_container=ProblemDetailsDTO,
            examples=[
                Example(
                    value=ErrorCodes.SERVICE_CONNECTION_ERROR.example(
                    "Не удалось подключиться к Redis",
                    ),
                )
            ],
        ),
    },
)
async def redis_health_check() -> JSONResponse:
    """Проверка подключения к Redis."""
    try:
        await redis_gateway.connect()
        _ = await redis_gateway._client.ping()
        return JSONResponse({"status": "ok", "redis": "connected"})
    except Exception as e:
        return JSONResponse(
            {"status": "error", "redis": f"failed: {str(e)}"},
            status_code=500, 
        ),

@get(
    "/health/all",
    summary="Проверка подключения ко всем сервисам",
    description="Эндпоинт проверяет возможность подключения ко всем сервисам (MongoDB, MinIO, Redis)",
    tags=["Дебаг"],
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
            data_container=ProblemDetailsDTO,
            examples=[
                Example(
                    value=ErrorCodes.SERVICE_CONNECTION_ERROR.example(
                        "Не удалось подключиться к одному или нескольким сервисам"
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
        await redis_gateway.connect()
        _ = await redis_gateway._client.ping()
    except Exception as e:
        errors["redis"] = f"failed: {str(e)}"
    
    if not errors:
        return JSONResponse({"status": "ok", "mongodb": "connected", "minio": "connected", "redis": "connected"})
    else:
        return JSONResponse({"status": "error", **errors}, status_code=500)