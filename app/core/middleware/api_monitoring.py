"""Middleware для мониторинга API."""
from __future__ import annotations

from collections.abc import Callable
from time import perf_counter

from litestar.types import ASGIApp, Receive, Scope, Send
from punq import Container

from app.monitoring.api_monitor import ApiMonitor


def api_monitor_middleware(container: Container) -> Callable[[ASGIApp], ASGIApp]:
    """ASGI middleware factory — использует ApiMonitor (если в контейнере нет, создаёт локально)."""

    def create_middleware(app: ASGIApp) -> ASGIApp:
        monitor: ApiMonitor
        try:
            monitor = container.resolve(ApiMonitor)
        except Exception:
            monitor = ApiMonitor()

        async def middleware(scope: Scope, receive: Receive, send: Send) -> None:
            """Создает middleware для счётчика."""
            if scope["type"] != "http":
                await app(scope, receive, send)
                return

            path = scope.get("path", "")
            method = scope.get("method", "UNKNOWN")

            start = perf_counter()
            status_code = 500

            async def send_wrapper(message: dict) -> None:
                """Wrapper."""
                nonlocal status_code
                if message.get("type") == "http.response.start":
                    status = message.get("status")
                    if isinstance(status, int):
                        status_code = status
                await send(message)

            await app(scope, receive, send_wrapper)
            latency_ms = (perf_counter() - start) * 1000.0
            monitor.record(path, method, status_code, latency_ms)

        return middleware

    return create_middleware
