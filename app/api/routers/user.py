"""Модуль содержит эндпоинты для работы с пользователями."""
# API_User

from litestar import post
from litestar.dto import DataclassDTO
from litestar.exceptions import HTTPException
from litestar.status_codes import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
)
from punq import Container

from app.api.schemas.user_dto import UserCreateDTO, UserDTO
from app.core.domain.models.user import User
from app.core.errors.auth import (
    EmailAlreadyTakenError,
    EmailValidationError,
    PasswordDontMatchError,
    UsernameAlreadyTakenError,
)
from app.core.errors.validation import (
    PasswordValidationError,
    UsernameValidationError,
)
from app.core.services.user_service import UserService


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
    """Эндпоинт создания пользователя.

    Args:
        data (UserCreateDTO): Данные для создания пользователя
        container (Container): Контейнер

    Returns:
        UserDTO: Данные пользователя
    """
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
        PasswordDontMatchError,
        PasswordValidationError,
        EmailValidationError,
        UsernameValidationError,
        EmailAlreadyTakenError,
        UsernameAlreadyTakenError,
    ) as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e)) from e
