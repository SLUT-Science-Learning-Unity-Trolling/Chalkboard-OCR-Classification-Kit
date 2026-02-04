"""Модуль содержит эндпоинты авторизации и выхода из профиля."""
# API_Auth

from typing import Any

from litestar import Response, get, post
from litestar.di import Provide
from litestar.dto import DataclassDTO
from litestar.exceptions import HTTPException
from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_204_NO_CONTENT,
)
from litestar.openapi import ResponseSpec
from litestar.openapi.spec import Example
from punq import Container

from app.api.schemas.problem_details_dto import ProblemDetailsDTO
from app.api.schemas.user_dto import UserDTO, UserLoginDTO
from app.config import config
from app.core.errors.auth import InvalidEmailOrPasswordError
from app.core.services.auth_service import AuthService


@post(
    "/auth/login",
    status_code=HTTP_200_OK,
    dto=DataclassDTO[UserLoginDTO],
    return_dto=DataclassDTO[UserDTO],
    responses = {
        HTTP_200_OK: ResponseSpec(
            description="Пользователь авторизован",
            data_container=UserDTO,
            examples=[
                Example(
                    value={
                        "id": "694de2b36e5be2ab74f350e6",
                        "username": "User123",
                        "email": "user@example.com",
                    },
                )
            ],
        ),
        HTTP_401_UNAUTHORIZED: ResponseSpec(
            description="Неверные данные",
            data_container=ProblemDetailsDTO,
            examples=[
                Example(
                    value={
                        "type": "Поменять на нормальный URL",
                        "title": "Неверные данные",
                        "status": 401,
                        "detail": "Неверная почта/логин или пароль",
                    },
                )
            ],
        ),
        HTTP_400_BAD_REQUEST: ResponseSpec(
            description="Невалидные данные",
            data_container=ProblemDetailsDTO,
             examples=[
                Example(
                    value={
                        "type": "Поменять на нормальный URL",
                        "title": "Невалидные данные",
                        "status": 400,
                        "detail": "Ошибка валидации данных",
                    },
                )
            ],
        ),
        HTTP_500_INTERNAL_SERVER_ERROR: ResponseSpec(
            description="Внутренняя ошибка сервера",
            data_container=ProblemDetailsDTO,
             examples=[
                Example(
                    value={
                        "type": "Поменять на нормальный URL",
                        "title": "Внутренняя ошибка сервера",
                        "status": 500,
                        "detail": "Произошла внутренняя ошибка сервера",
                    },
                )
            ],
        ),
    },
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

        user_dto = UserDTO.fromrow(user.__dict__)

        response = Response(user_dto)
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
            status_code=HTTP_401_UNAUTHORIZED, detail="Неверная почта/логин или пароль"
        ) from None


@post(
    "/auth/logout", 
    status_code=HTTP_200_OK,
    responses = {
        HTTP_200_OK: ResponseSpec(
            description="Пользователь успешно вышел из аккаунта",
            data_container=None,
        ),
    },
)
async def logout_user() -> Response:
    """Эндпоинт выхода из профиля.

    Удаляет JWT из cookie, разлогинивая пользователя.
    """
    response = Response(
        content={"detail": "Пользователь успешно вышел из аккаунта"},
        status_code=HTTP_200_OK,
    )
    response.delete_cookie(
        key="token",
        path="/",
    )

    return response


@get(
    "/me",
    dependencies={"current_user": Provide(AuthService.get_current_user)},
    status_code=HTTP_200_OK,
    responses = {
        HTTP_200_OK: ResponseSpec(
            description="Пользователь авторизован",
            data_container=UserDTO,
            examples=[
                Example(
                    value={
                        "id": "694de2b36e5be2ab74f350e6",
                        "username": "User123",
                        "email": "user@example.com",
                    },
                )
            ],
        ),
        HTTP_401_UNAUTHORIZED: ResponseSpec(
            description="Пользователь не авторизован",
            data_container=ProblemDetailsDTO,
            examples=[
                Example(
                    value={
                        "type": "Поменять на нормальный URL",
                        "title": "Пользователь не авторизован",
                        "status": 401,
                        "detail": "Пользователь не авторизован",
                    },
                )
            ],
        ),
    },
)
async def get_me(current_user: UserDTO | None) -> UserDTO:
    """Эндпоинт возвращает данные текущего пользователя."""
    if not current_user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Пользователь не авторизован",
        )

    return current_user
