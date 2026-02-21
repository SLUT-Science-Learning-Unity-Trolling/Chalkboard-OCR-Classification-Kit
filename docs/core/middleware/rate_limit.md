# Модуль rate_limit

Middleware для rate limiting.

## def rate_limit_middleware:
#### Middleware для rate limiting.
Разделяет лимиты на login, refresh и остальные запросы.

```python
def rate_limit_middleware(container: Container) -> Callable[[ASGIApp], ASGIApp]:
    """Middleware для rate limiting.

    Разделяет лимиты на login, refresh и остальные запросы.
    """

    def create_middleware(app: ASGIApp) -> ASGIApp:
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
```
---