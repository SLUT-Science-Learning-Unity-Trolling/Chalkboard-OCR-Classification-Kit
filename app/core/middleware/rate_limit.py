"""Middleware для rate limiting."""

from collections.abc import Callable
from typing import Optional

from litestar.connection import Request
from litestar.types import ASGIApp, Receive, Scope, Send
from punq import Container

from app.adapters.repositories.redis_rate_limit_repo import RedisRateLimitRepo
from app.core.errors.security import TooManyRequestsError


def rate_limit_middleware(container: Container) -> Callable[[ASGIApp], ASGIApp]:
    """Фабрика ASGI middleware для rate limiting.

    Middleware извлекает `RedisRateLimitRepo` из DI-контейнера для проверки лимитов.

    Args:
        container (Container): DI-контейнер с сервисами приложения.

    Returns:
        Callable[[ASGIApp], ASGIApp]: Функция, принимающая ASGI-приложение и возвращающая обёрнутое приложение с rate-limit проверкой.
    """

    def create_middleware(app: ASGIApp) -> ASGIApp:
        """Создаёт middleware для ограничения количества запросов.

        Логика middleware:
            - Обрабатывает только HTTP-запросы.
            - Получает IP клиента через request.client или заголовок X-Forwarded-For.
            - Определяет лимиты в зависимости от пути запроса:
                * /auth/login → 15 запросов / 15 минут
                * /auth/refresh → 15 запросов / 15 минут
                * остальные → 120 запросов / 1 минута
            - Проверяет лимит через RedisRateLimitRepo.
            - Если лимит превышен, генерирует TooManyRequestsError с retry_after.
            - Иначе пропускает запрос дальше.

        Args:
            app (ASGIApp): ASGI-приложение для обёртывания.

        Returns:
            ASGIApp: Обёрнутое приложение с проверкой лимитов запросов.
        """
        async def middleware(scope: Scope, receive: Receive, send: Send) -> None:
            if scope["type"] != "http":
                await app(scope, receive, send)
                return

            try:
                request = Request(scope, receive)
            except Exception:
                await app(scope, receive, send)
                return

            redis_rate_limit: RedisRateLimitRepo = container.resolve(RedisRateLimitRepo)

            client_ip: str | None = None
            client_ip = getattr(request.client, "host", None) if getattr(request, "client", None) else None
            if not client_ip:
                xff = request.headers.get("x-forwarded-for")
                if xff:
                    client_ip = xff.split(",")[0].strip()
                else:
                    client_ip = scope.get("client")[0] if scope.get("client") else "unknown"

            path = scope.get("path", "")
            if path.startswith("/auth/login"):
                limit, window, action = 15, 900, "login"
            elif path.startswith("/auth/refresh"):
                limit, window, action = 15, 900, "refresh"
            else:
                limit, window, action = 120, 60, "general"

            try:
                allowed, retry_after = await redis_rate_limit.is_allowed(
                    client_ip, action, limit, window
                )
            except Exception:
                await app(scope, receive, send)
                return

            if not allowed:
                raise TooManyRequestsError("Превышен лимит запросов", retry_after=retry_after)

            await app(scope, receive, send)

        return middleware

    return create_middleware