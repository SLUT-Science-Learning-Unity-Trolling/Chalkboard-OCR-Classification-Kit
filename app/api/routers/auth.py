from typing import Any
from litestar import Response, get, post
from litestar.dto import DataclassDTO
from litestar.exceptions import HTTPException
from litestar.status_codes import (
    HTTP_201_CREATED,
    HTTP_200_OK,
)
from litestar.di import Provide
from punq import Container

from app.core.services.auth_service import AuthService

from app.api.schemas.user_dto import UserDTO, UserLoginDTO


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
    """Эндпоинт для авторизации пользователя с установкой JWT в cookie."""
    auth_service = container.resolve(AuthService)
    try:
        user, token = await auth_service.auth_existing_user(
            email=data.email, password=data.password
        )

        response = Response({"user": UserDTO.fromrow(user.__dict__)})
        response.set_cookie(
            key="token",
            value=token,
            httponly=True,
            secure=True,
            samesite="strict",
            path="/",
        )
        return response

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Internal server error occurred"
        )


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


@get(
    "/me", dependencies={"current_user": Provide(AuthService.get_current_user)}
)
async def get_me(current_user: UserDTO | None) -> dict[str, Any]:
    """Эндпоинт возвращает данные текущего пользователя."""
    if current_user:
        return {"success": True, "user": current_user}

    return {
        "success": False,
        "message": "Пользователь не зарегистрирован или не найден в системе",
    }
