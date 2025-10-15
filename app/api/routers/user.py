"""Модуль содержит эндпоинты для работы с пользователями."""

# API_User
from typing import Annotated

from bson import ObjectId
from litestar import delete, get, post
from litestar.datastructures import UploadFile
from litestar.di import Provide
from litestar.dto import DataclassDTO
from litestar.enums import RequestEncodingType
from litestar.exceptions import HTTPException
from litestar.params import Body
from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
)
from punq import Container

from app.api.schemas.image_dto import ImageDTO
from app.api.schemas.user_dto import UserCreateDTO, UserDTO
from app.core.domain.models.image import UploadedImage
from app.core.domain.models.user import User
from app.core.errors.auth import (
    EmailAlreadyTakenError,
    EmailValidationError,
    PasswordDontMatchError,
    UsernameAlreadyTakenError,
)
from app.core.errors.user import AbsentUserError, DeleteImageError, ImageUploadError
from app.core.errors.validation import (
    ImageExtensionValidationError,
    PasswordValidationError,
    UsernameValidationError,
)
from app.core.services.auth_service import AuthService
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


@post(
    "/users/upload_image",
    status_code=HTTP_201_CREATED,
    return_dto=DataclassDTO[ImageDTO],
    dependencies={"current_user": Provide(AuthService.get_current_user)},
)
async def upload_image(
    container: Container,
    current_user: UserDTO,
    data: Annotated[UploadFile, Body(media_type=RequestEncodingType.MULTI_PART)],
) -> ImageDTO:
    """Эндпоинт загрузки локального изображения пользователя через UploadFile.

    Args:
        container (Container): Контейнер
        current_user (UserDTO): Пользователь
        data (UploadFile): Файл изображения

    Returns:
        ImageDTO: Данные изображения
    """
    user_service = container.resolve(UserService)
    try:
        user_id = current_user.id
    except AbsentUserError:
        raise AbsentUserError("Не выполнен вход в аккаунт") from None

    try:
        image: UploadedImage = await user_service.upload_image(
            user_id=user_id, file=data
        )

        image_dict = image.__dict__.copy()
        if "_id" in image_dict and isinstance(image_dict["_id"], ObjectId):
            image_dict["_id"] = str(image_dict["_id"])

        return ImageDTO.fromrow(image_dict)

    except (
        ImageExtensionValidationError,
        ImageUploadError,
    ) as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e)) from e


@get(
    "users/get_all_user_images",
    status_code=HTTP_201_CREATED,
    return_dto=DataclassDTO[ImageDTO],
    dependencies={"current_user": Provide(AuthService.get_current_user)},
)
async def get_all_user_images(
    container: Container,
    current_user: UserDTO,
) -> list[ImageDTO]:
    """Эндпоинт получения всех изображений пользователя.

    Args:
        container (Container): Контейнер
        current_user (UserDTO): Пользователь

    Returns:
        list[ImageDTO]: Список изображений пользователя
    """
    user_service = container.resolve(UserService)
    try:
        user_id = current_user.id
    except AbsentUserError:
        raise AbsentUserError("Не выполнен вход в аккаунт") from None

    try:
        images: list[UploadedImage] = await user_service.get_all_user_images(
            user_id=user_id
        )
        return [ImageDTO.fromrow(image.__dict__) for image in images]

    except ImageUploadError as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e)) from e


@delete(
    "users/delete_image",
    status_code=HTTP_200_OK,
    dependencies={"current_user": Provide(AuthService.get_current_user)},
)
async def delete_image(
    container: Container,
    current_user: UserDTO,
    url: str,
) -> dict[str, str]:
    """Эндпоинт удаления изображения пользователя.

    Args:
        container (Container): Контейнер
        current_user (UserDTO): Пользователь
        url (str): Путь к изображению

    Returns:
        dict[str, str]: Сообщение об успешном удалении изображения
    """
    user_service = container.resolve(UserService)

    try:
        user_id = current_user.id
    except AbsentUserError as e:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=f"Не выполнен вход в аккаунт: {e}"
        ) from e

    try:
        await user_service.delete_image(user_id=user_id, url=url)
        return {"success": "true", "message": "Изображение успешно удалено"}
    except DeleteImageError as e:
        return {"success": "false", "message": f"Ошибка при удалении изображения: {e}"}
    except Exception as e:
        return {"success": "false", "message": f"Произошла непредвиденная ошибка: {e}"}
