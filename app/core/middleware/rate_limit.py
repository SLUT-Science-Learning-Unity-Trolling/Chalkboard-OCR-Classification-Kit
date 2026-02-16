from collections.abc import Callable
from litestar.connection import Request
from litestar.types import ASGIApp, Receive, Scope, Send
from punq import Container
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_429_TOO_MANY_REQUESTS

from app.adapters.repositories.redis_rate_limit_repo import RedisRateLimitRepo

def rate_limit_middleware(container: Container) -> Callable[[ASGIApp], ASGIApp]:
    """
    Middleware для rate limiting.
    Разделяет лимиты на login, refresh и остальные запросы.
    """

    def create_middleware(app: ASGIApp) -> ASGIApp:
        async def middleware(scope: Scope, receive: Receive, send: Send) -> None:
            if scope["type"] != "http":
                await app(scope, receive, send)
                return

            request = Request(scope, receive)
            redis_rate_limit: RedisRateLimitRepo = container.resolve(RedisRateLimitRepo)

            client_ip = request.client.host

            if scope["path"].startswith("/auth/login"):
                limit, window, action = 15, 900, "login"
            elif scope["path"].startswith("/auth/refresh"):
                limit, window, action = 15, 900, "refresh"
            else:
                limit, window, action = 120, 60, "general"

            allowed = await redis_rate_limit.is_allowed(client_ip, action, limit, window)
            if not allowed:
                raise HTTPException(
                    status_code=HTTP_429_TOO_MANY_REQUESTS,
                    detail="Слишком много запросов, повторите позже."
                )

            await app(scope, receive, send)

        return middleware

    return create_middleware
