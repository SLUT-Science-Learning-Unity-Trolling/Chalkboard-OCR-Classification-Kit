"""Модуль для запуска сервера."""
# Main

from litestar import Litestar
from litestar.config.cors import CORSConfig
from litestar.openapi import OpenAPIConfig

from app.api.exceptions.handlers import EXCEPTION_HANDLERS
from app.api.routers import api_routers
from app.config import config
from app.container import build_container
from app.core.middleware.api_monitoring import api_monitor_middleware
from app.core.middleware.paseto_refresh import access_token_middleware
from app.core.middleware.rate_limit import rate_limit_middleware
from app.monitoring.prometheus_middleware import PrometheusMiddleware

if config.DEBUG:
    pass

container = build_container()

openapi_config = OpenAPIConfig(
    title="COCK API",
    version="2.0.0",
    summary="API для сервиса Chalkboard OCR Classification Kit",
    description="""
Готовый к продакшену  OCR API

Особенности
 - PASETO токены
 - MongoDB основное хранилище данных
 - Чёрный список токенов и rate limit через Redis
 - Отдельные движки для распознавания формул и текста, переключаемые изменением одной строки кода
""",
    contact={"name": "ProudRykar", "email": "proudrykar@mail.ru"},
    license={"name": "MIT License", "url": "https://opensource.org/licenses/MIT"},
    enabled_endpoints=["swagger", "redoc", "elements", "openapi.json"],
)

cors_config = CORSConfig(
    allow_origins=["http://localhost:5173", "http://178.213.116.90:5173"],
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
        PrometheusMiddleware(),
        access_token_middleware(container=container),
        rate_limit_middleware(container=container),
        api_monitor_middleware(container=container),

    ],
    exception_handlers=EXCEPTION_HANDLERS,
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="debug")
