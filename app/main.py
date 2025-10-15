"""Модуль для запуска сервера."""
# Main

from litestar import Litestar
from litestar.openapi import OpenAPIConfig

from app.api.routers.auth import auth_user, get_me, logout_user
from app.api.routers.health import (
    db_health_check,
    minio_health_check,
    server_health_check,
)
from app.api.routers.user import create_user
from app.container import build_container


openapi_config = OpenAPIConfig(
    title="COCK API",
    version="1.0.0",
    description="Chalkboard OCR Classification Kit API",
    enabled_endpoints=["swagger", "redoc", "elements", "openapi.json"],
)

app = Litestar(
    route_handlers=[
        server_health_check,
        db_health_check,
        minio_health_check,
        create_user,
        auth_user,
        logout_user,
        get_me,
    ],
    dependencies={"container": build_container},
    openapi_config=openapi_config,
    debug=True,
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="debug")
