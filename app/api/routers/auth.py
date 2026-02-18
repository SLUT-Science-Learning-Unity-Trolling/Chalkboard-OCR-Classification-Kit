"""Модуль содержит эндпоинты авторизации и выхода из профиля."""
# API_Auth

import paseto

from litestar import Request, Response, Router, get, post
from litestar.di import Provide
from litestar.dto import DataclassDTO
from litestar.exceptions import HTTPException
from litestar.openapi import ResponseSpec
from litestar.openapi.spec import Example
from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_429_TOO_MANY_REQUESTS,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from punq import Container

from app.adapters.repositories.redis_blacklist_repo import RedisBlacklistRepo
from app.api.exceptions.problem_details_dto import ProblemDetailsDTO
from app.api.exceptions.problem_factory import ErrorCodes
from app.api.schemas.user_dto import UserDTO, UserLoginDTO
from app.config import config, token_key
from app.core.errors.auth import InvalidEmailOrPasswordError, UnauthorizedError
from app.core.errors.security import TooManyRequestsError
from app.core.services.auth_service import AuthService


@post(
    "/login",
    summary="Авторизация пользователя",
    description="Эндпоинт для авторизации пользователя с установкой Paseto в cookie."
    "Принимает email или username и пароль, возвращает данные пользователя и устанавливает access и refresh токены в cookie.",
    tags=["Авторизация"],
    status_code=HTTP_200_OK,
    dto=DataclassDTO[UserLoginDTO],
    return_dto=DataclassDTO[UserDTO],
    responses={
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
                    value=ErrorCodes.AUTHENTICATION_ERROR.example(
                        "Неверная почта/логин или пароль"
                    ),
                )
            ],
        ),
        HTTP_400_BAD_REQUEST: ResponseSpec(
            description="Невалидные данные",
            data_container=ProblemDetailsDTO,
            examples=[
                Example(
                    value=ErrorCodes.VALIDATION_ERROR.example(
                        "Ошибка валидации данных"
                    ),
                )
            ],
        ),
        HTTP_500_INTERNAL_SERVER_ERROR: ResponseSpec(
            description="Внутренняя ошибка сервера",
            data_container=ProblemDetailsDTO,
            examples=[
                Example(
                    value=ErrorCodes.SERVICE_CONNECTION_ERROR.example(
                        "Внутренняя ошибка сервера"
                    ),
                )
            ],
        ),
        HTTP_429_TOO_MANY_REQUESTS: ResponseSpec(
            description="Слишком много запросов",
            data_container=ProblemDetailsDTO,
            examples=[
                Example(
                    value=ErrorCodes.TOO_MANY_REQUESTS_ERROR.example(
                        "Слишком много попыток авторизации. Попробуйте позже."
                    ),
                )
            ],
        ),
    },
)
async def auth_user(
    data: UserLoginDTO,
    container: Container,
    request: Request,
) -> Response:
    """Эндпоинт для авторизации пользователя с установкой PASETO в cookie.

    Args:
        data (UserLoginDTO): Данные для авторизации пользователя
        container (Container): Контейнер
        request (Request): HTTP запрос для получения IP клиента

    Returns:
        Response: Ответ с PASETO в cookie
    """
    auth_service = container.resolve(AuthService)

    client_ip = request.client.host

    try:
        user, access_token, refresh_token = await auth_service.auth_existing_user(
            identifier=data.identifier,
            password=data.password,
            client_ip=client_ip,
        )

        user_dto = UserDTO.fromrow(user.__dict__)

        response = Response(user_dto)

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            max_age=config.ACCESS_TOKEN_EXPIRE_TIME,
            samesite="strict",
            path="/",
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            max_age=config.REFRESH_TOKEN_EXPIRE_TIME,
            samesite="strict",
            path="/",
        )
        return response

    except InvalidEmailOrPasswordError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Неверная почта/логин или пароль"
        ) from None

    except TooManyRequestsError:
        raise HTTPException(
            status_code=HTTP_429_TOO_MANY_REQUESTS,
            detail="Слишком много попыток авторизации. Попробуйте позже.",
        ) from None


@post(
    "/logout",
    summary="Выход из профиля",
    description="Эндпоинт выхода из профиля. Удаляет Paseto из cookie",
    tags=["Авторизация"],
    status_code=HTTP_200_OK,
    responses={
        HTTP_200_OK: ResponseSpec(
            description="Пользователь успешно вышел из аккаунта",
            data_container=None,
        ),
    },
)
async def logout_user(request: Request, container: Container) -> Response:
    """Эндпоинт выхода из профиля.

    Удаляет PASETO из cookie и заносит refresh (и access) токены в blacklist.
    """
    redis_repo: RedisBlacklistRepo = container.resolve(RedisBlacklistRepo)

    async def _blacklist_token(token: str, expected_type: str, expires_in: int) -> None:
        """Парсит токен и добавляет его jti в blacklist, если валиден."""
        try:
            parsed = paseto.parse(key=token_key, purpose="local", token=token)
            claims = parsed["message"]

            if claims.get("type") == expected_type:
                jti = claims.get("jti")
                if jti and redis_repo:
                    await redis_repo.add_to_blacklist(jti, expires_in=expires_in)
        except Exception:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail="Невалидный токен"
            ) from None

    refresh_token = request.cookies.get("refresh_token")
    access_token = request.cookies.get("access_token")

    if refresh_token:
        await _blacklist_token(
            token=refresh_token,
            expected_type="refresh",
            expires_in=config.REFRESH_TOKEN_EXPIRE_TIME,
        )

    if access_token:
        await _blacklist_token(
            token=access_token,
            expected_type="access",
            expires_in=config.ACCESS_TOKEN_EXPIRE_TIME,
        )

    response = Response(
        content={"detail": "Пользователь успешно вышел из аккаунта"},
        status_code=HTTP_200_OK,
    )
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")

    return response


@get(
    "/me",
    summary="Данные текущего пользователя",
    description="Эндпоинт возвращает данные текущего авторизованного пользователя",
    tags=["Debug", "Авторизация"],
    dependencies={"current_user": Provide(AuthService.get_current_user)},
    status_code=HTTP_200_OK,
    responses={
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
                    value=ErrorCodes.AUTHORIZATION_ERROR.example(
                        "Пользователь не авторизован или сессия истекла"
                    ),
                )
            ],
        ),
        HTTP_429_TOO_MANY_REQUESTS: ResponseSpec(
            description="Слишком много запросов",
            data_container=ProblemDetailsDTO,
            examples=[
                Example(
                    value=ErrorCodes.TOO_MANY_REQUESTS_ERROR.example(
                        "Слишком много попыток авторизации. Попробуйте позже."
                    ),
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
            detail="Пользователь не авторизован или сессия истекла",
        )

    return current_user


@post(
    "/refresh",
    summary="Обновление access токена",
    description="Эндпоинт обновляет access токен по refresh токену",
    status_code=HTTP_200_OK,
    tags=["Авторизация"],
    responses={
        HTTP_200_OK: ResponseSpec(
            description="Токены успешно обновлены",
            data_container=None,
        ),
        HTTP_401_UNAUTHORIZED: ResponseSpec(
            description="Невалидный refresh токен",
            data_container=ProblemDetailsDTO,
            examples=[
                Example(
                    value=ErrorCodes.AUTHENTICATION_ERROR.example(
                        "Невалидный или просроченный refresh токен"
                    ),
                )
            ],
        ),
        HTTP_429_TOO_MANY_REQUESTS: ResponseSpec(
            description="Слишком много попыток авторизации",
            data_container=ProblemDetailsDTO,
            examples=[
                Example(
                    value=ErrorCodes.TOO_MANY_REQUESTS_ERROR.example(
                        "Слишком много попыток обновления токенов. Попробуйте позже."
                    ),
                )
            ],
        ),
    },
)
async def refresh_user(request: Request, container: Container) -> Response:
    """Эндпоинт обновляет access токен по refresh токену.

    Получает refresh токен из cookie, проверяет его валидность и выдает новый access токен.

    Args:
        request (Request): HTTP запрос с refresh токеном в
        container (Container): Контейнер для получения сервисов

    Returns:
        Response: Ответ с новым access токеном в cookie

    Raises:
        HTTPException: 401 если refresh токен не валиден или отсутствует
        HTTPException: 429 если слишком много попыток обновления токенов
    """
    auth_service = container.resolve(AuthService)

    client_ip = request.client.host

    refresh_token = request.cookies.get("refresh_token")
    access_token = request.cookies.get("access_token")
    if not refresh_token:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Нет refresh токена"
        )

    try:
        new_access, new_refresh = await auth_service.refresh_tokens(
            refresh_token, access_token, client_ip
        )

        response = Response({"detail": "Token refreshed"})

        response.set_cookie(
            key="access_token",
            value=new_access,
            httponly=True,
            secure=True,
            max_age=config.ACCESS_TOKEN_EXPIRE_TIME,
            samesite="strict",
            path="/",
        )

        response.set_cookie(
            key="refresh_token",
            value=new_refresh,
            httponly=True,
            secure=True,
            max_age=config.REFRESH_TOKEN_EXPIRE_TIME,
            samesite="strict",
            path="/",
        )

        return response

    except TooManyRequestsError:
        raise HTTPException(
            status_code=HTTP_429_TOO_MANY_REQUESTS,
            detail="Слишком много попыток обновления токенов. Попробуйте позже.",
        ) from None

    except UnauthorizedError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Невалидный или просроченный refresh токен",
        ) from None


auth_router = Router(
    path="/auth",
    route_handlers=[
        auth_user,
        logout_user,
        refresh_user,
        get_me,
    ],
    tags=["Авторизация"],
)
