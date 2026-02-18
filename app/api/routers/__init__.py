"""Объединение всех роутеров API."""

from litestar import Router

from .auth import auth_router
from .health import health_router
from .ocr import ocr_router
from .user import users_router


api_routers = Router(
    path='',
    route_handlers=[
    health_router,
    auth_router,
    users_router,
    ocr_router,
    ],
)
