# -*- coding: utf-8 -*-
# API_Health

from litestar import get
from litestar.status_codes import HTTP_200_OK
from pymongo import AsyncMongoClient
from pymongo.errors import ConnectionFailure
from starlette.responses import JSONResponse

from app.config import Config

client = AsyncMongoClient(Config.DATABASE_URL)


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
