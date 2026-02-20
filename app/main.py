"""Модуль для запуска сервера."""
# Main

from litestar import Litestar
from litestar.config.cors import CORSConfig
from litestar.openapi import OpenAPIConfig

from app.api.routers import api_routers
from app.config import config
from app.container import build_container
from app.core.middleware.api_monitoring import api_monitor_middleware
from app.core.middleware.paseto_refresh import access_token_middleware
from app.core.middleware.rate_limit import rate_limit_middleware


if config.DEBUG:
    pass

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
    route_handlers=[api_routers],
    dependencies={"container": build_container},
    openapi_config=openapi_config,
    debug=True,
    cors_config=cors_config,
    middleware=[
        access_token_middleware(container=container),
        rate_limit_middleware(container=container),
        api_monitor_middleware(container=container),
    ],
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="debug")
