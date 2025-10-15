"""Модуль содержит эндпоинты для проверки работы сервера и подключения к MongoDB."""
# API_Health

from litestar import get
from litestar.status_codes import HTTP_200_OK
from pymongo import AsyncMongoClient
from pymongo.errors import ConnectionFailure
from starlette.responses import JSONResponse

from app.adapters.gateways.s3 import MinioGateway
from app.config import Config


client = AsyncMongoClient(Config.DATABASE_URL)
minio_gateway = MinioGateway()


@get("/health/server", status_code=HTTP_200_OK)
def server_health_check() -> JSONResponse:
    """Проверка работы сервера.

    Returns:
        JSONResponse: Ответ
    """
    return JSONResponse({"status": "ok"})


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
