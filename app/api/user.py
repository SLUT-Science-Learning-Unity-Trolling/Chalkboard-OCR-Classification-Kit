from litestar import post
from litestar.dto import DataclassDTO
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
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
) -> UserDTO:
    """Эндпоинт для авторизации пользователя."""
    auth_service = container.resolve(AuthService)
    try:
        user = await auth_service.auth_existing_user(
            email=data.email, password=data.password
        )
        return UserDTO(id=user.id, username=user.username, email=user.email)

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Internal server error occurred"
        )
