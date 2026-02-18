"""Модуль содержит эндпоинты для проверки работы сервера и подключения к сервисам."""
# API_Health

from litestar import Router, get
from litestar.openapi import ResponseSpec
from litestar.openapi.spec import Example
from litestar.status_codes import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR
from pymongo import AsyncMongoClient
from pymongo.errors import ConnectionFailure
from redis import Redis
from starlette.responses import JSONResponse

from app.adapters.gateways.redis import RedisGateway
from app.adapters.gateways.s3 import MinioGateway
from app.api.exceptions.problem_details_dto import ProblemDetailsDTO
from app.api.exceptions.problem_factory import ErrorCodes
from app.config import Config


client = AsyncMongoClient(Config.DATABASE_URL)
minio_gateway = MinioGateway()
redis_blacklist_gateway = RedisGateway(db=Config.REDIS_TOKENS_BLACKLIST_DB)
redis_rate_limit_gateway = RedisGateway(db=Config.REDIS_RATE_LIMITING_DB)


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


health_router = Router(
    path="/health",
    tags=["Debug"],
    route_handlers=[
        server_health_check,
        db_health_check,
        minio_health_check,
        redis_health_check,
        all_services_health_check,
    ],
)
