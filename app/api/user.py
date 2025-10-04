from litestar import Response, post
from litestar.dto import DataclassDTO
from litestar.exceptions import HTTPException
from litestar.status_codes import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_200_OK,
)
from punq import Container

from app.core.models.user import User
from app.core.services.auth_service import AuthService
from app.core.services.user_service import UserService
from app.errors.auth import (
    EmailAlreadyTaken,
    EmailValidationError,
    PasswordDontMatch,
)
from app.errors.security import PasswordValidationError
from app.schema.user_dto import UserCreateDTO, UserDTO, UserLoginDTO


@post(
    "/users/create",
    status_code=HTTP_201_CREATED,
    dto=DataclassDTO[UserCreateDTO],
    return_dto=DataclassDTO[UserDTO],
)
async def create_user(
    data: UserCreateDTO,
    container: Container,
) -> UserDTO:
    """Эндпоинт создания пользователя."""
    user_service = container.resolve(UserService)
    try:
        user: User = await user_service.create_user(
            username=data.username,
            email=data.email,
            password=data.password,
            repeat_password=data.repeat_password,
        )
        return UserDTO.fromrow(user.__dict__)

    except (
        PasswordDontMatch,
        PasswordValidationError,
        EmailValidationError,
        EmailAlreadyTaken,
    ) as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))


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
