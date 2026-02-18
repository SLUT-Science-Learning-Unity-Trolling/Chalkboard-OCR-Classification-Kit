"""Blank."""

from collections.abc import Callable

import paseto

from litestar.connection import Request
from litestar.datastructures import MutableScopeHeaders
from litestar.types import ASGIApp, Message, Receive, Scope, Send
from punq import Container

from app.api.schemas.user_dto import UserDTO
from app.config import config
from app.core.services.auth_service import AuthService


def access_token_middleware(container: Container) -> Callable[[ASGIApp], ASGIApp]:
    """Middleware проверяет access_token из cookie и подставляет current_user.

    Если токен отсутствует или невалидный → просто пропускает запрос без user.
    """

    def create_middleware(app: ASGIApp) -> ASGIApp:
        async def middleware(scope: Scope, receive: Receive, send: Send) -> None:
            if scope["type"] != "http":
                await app(scope, receive, send)
                return

            request = Request(scope, receive)
            auth_service = container.resolve(AuthService)
            current_user: UserDTO | None = None

            key = config.TOKEN_SECRET_KEY

            access_token = request.cookies.get("access_token")
            if access_token:
                try:
                    parsed = paseto.parse(
                        key=key,
                        purpose="local",
                        token=access_token,
                    )
                    claims = parsed["message"]

                    if claims.get("type") == "access":
                        user_id = claims["sub"]
                        current_user = await auth_service.get_user_by_id(user_id)

                except Exception:
                    current_user = None

            scope["current_user"] = current_user

            async def send_wrapper(message: Message) -> None:
                if message["type"] == "http.response.start":
                    headers = MutableScopeHeaders.from_message(message)
                    headers.add("access-control-allow-origin", "http://localhost:3000")
                    headers.add("access-control-allow-credentials", "true")

                await send(message)

            await app(scope, receive, send_wrapper)

        return middleware

    return create_middleware
