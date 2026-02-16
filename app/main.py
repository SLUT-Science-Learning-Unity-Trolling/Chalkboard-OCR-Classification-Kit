"""Модуль для запуска сервера."""
# Main

from litestar import Litestar
from litestar.openapi import OpenAPIConfig
from litestar.config.cors import CORSConfig

from app.api.routers.auth import auth_user, get_me, logout_user, refresh_user
from app.api.routers.health import (
    all_services_health_check,
    db_health_check,
    minio_health_check,
    redis_health_check,
    server_health_check,
)
from app.api.routers.user import (
    create_user,
    delete_image,
    get_all_user_images,
    upload_image,
)
from app.api.routers.ocr import ocr_to_pdf
from app.container import build_container
from app.core.middleware.paseto_refresh import access_token_middleware
from app.core.middleware.rate_limit import rate_limit_middleware

container = build_container()


openapi_config = OpenAPIConfig(
    title="COCK API",
    version="1.5.0",
    summary="API для сервиса Chalkboard OCR Classification Kit",
    description="""
Готовый к продакшену  OCR API

Фичи:
 - PASETO токены
 - MongoDB основное хранилище данных 
 - Хранение изображений в MinIO
 - Чёрный список токенов в Redis
""",
    contact={"name": "ProudRykar", "email": "proudrykar@mail.ru"},
    license={"name": "MIT License", "url": "https://opensource.org/licenses/MIT"},
    enabled_endpoints=["swagger", "redoc", "elements", "openapi.json"],
)

cors_config = CORSConfig(
    allow_origins=["http://localhost:5173"], 
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    allow_credentials=True,
)

app = Litestar(
    route_handlers=[
        server_health_check,
        db_health_check,
        minio_health_check,
        redis_health_check,
        all_services_health_check,
        create_user,
        upload_image,
        get_all_user_images,
        delete_image,
        auth_user,
        logout_user,
        get_me,
        ocr_to_pdf,
        refresh_user,
    ],
    dependencies={"container": build_container},
    openapi_config=openapi_config,
    debug=True,
    cors_config=cors_config,
    middleware=[access_token_middleware(container=container), rate_limit_middleware(container=container)],
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="debug")
