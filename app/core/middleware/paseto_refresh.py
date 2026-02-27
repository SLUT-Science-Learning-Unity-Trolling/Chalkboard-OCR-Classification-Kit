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
    """Фабрика ASGI middleware для проверки access_token и подстановки current_user.

    Извлекает сервис AuthService из DI-контейнера для получения пользователя по id из токена.

    Args:
        container (Container): DI-контейнер с сервисами приложения.

    Returns:
        Callable[[ASGIApp], ASGIApp]: Функция, принимающая ASGI-приложение и возвращающая обёрнутое приложение с middleware.
    """

    def create_middleware(app: ASGIApp) -> ASGIApp:
        """Создаёт middleware для обработки access_token.

        Логика middleware:
            - Проверка типа запроса (только HTTP).
            - Получение токена из cookie.
            - Валидация токена с помощью PASETO.
            - Подстановка current_user в scope.
            - Добавление CORS-заголовков при ответе.

        Args:
            app (ASGIApp): ASGI-приложение для обёртывания.

        Returns:
            ASGIApp: Обёрнутое приложение с подстановкой current_user.
        """

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
                """Wrapper для перехвата HTTP-ответа и добавления заголовков.

                Args:
                    message (Message): ASGI-сообщение.
                """
                if message["type"] == "http.response.start":
                    headers = MutableScopeHeaders.from_message(message)
                    headers.add("access-control-allow-origin", "http://localhost:3000")
                    headers.add("access-control-allow-credentials", "true")

                await send(message)

            await app(scope, receive, send_wrapper)

        return middleware

    return create_middleware
