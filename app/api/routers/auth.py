"""Модуль содержит эндпоинты авторизации и выхода из профиля."""
# API_Auth

from typing import Any

from litestar import Response, get, post
from litestar.di import Provide
from litestar.dto import DataclassDTO
from litestar.exceptions import HTTPException
from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
)
from punq import Container

from app.api.schemas.user_dto import UserDTO, UserLoginDTO
from app.config import config
from app.core.errors.auth import InvalidEmailOrPasswordError
from app.core.services.auth_service import AuthService


@post(
    "/auth/login",
    status_code=HTTP_201_CREATED,
    dto=DataclassDTO[UserLoginDTO],
    return_dto=DataclassDTO[UserDTO],
)
async def auth_user(
    data: UserLoginDTO,
    container: Container,
) -> Response:
    """Эндпоинт для авторизации пользователя с установкой JWT в cookie.

    Args:
        data (UserLoginDTO): Данные для авторизации пользователя
        container (Container): Контейнер

    Returns:
        Response: Ответ с JWT в cookie
    """
    auth_service = container.resolve(AuthService)

    try:
        user, token = await auth_service.auth_existing_user(
            identifier=data.identifier,
            password=data.password,
        )

        response = Response({"user": UserDTO.fromrow(user.__dict__)})
        response.set_cookie(
            key="token",
            value=token,
            httponly=True,
            secure=True,
            expires=config.JWT_EXPIRE_TIME,
            samesite="strict",
            path="/",
        )
        return response

    except InvalidEmailOrPasswordError:
        raise HTTPException(
            status_code=500, detail="Internal server error occurred"
        ) from None


@post("/auth/logout", status_code=HTTP_200_OK)
async def logout_user() -> Response:
    """Эндпоинт выхода из профиля.

    Удаляет JWT из cookie, разлогинивая пользователя.
    """
    response = Response({"detail": "Logged out successfully"})
    response.delete_cookie(
        key="token",
        path="/",
    )

    return response


@get("/me", dependencies={"current_user": Provide(AuthService.get_current_user)})
async def get_me(current_user: UserDTO | None) -> dict[str, Any]:
    """Эндпоинт возвращает данные текущего пользователя.

    Args:
        current_user (UserDTO | None): Пользователь

    Returns:
        dict[str, Any]: Данные пользователя
    """
    if current_user:
        return {"success": True, "user": current_user}

    return {
        "success": False,
        "message": "Пользователь не зарегистрирован или не найден в системе",
    }
