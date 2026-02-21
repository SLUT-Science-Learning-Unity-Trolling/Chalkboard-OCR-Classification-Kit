"""Модуль содержит эндпоинты для работы с пользователями."""

# API_User

from typing import Annotated

from bson import ObjectId
from litestar import Router, delete, get, post
from litestar.datastructures import UploadFile
from litestar.di import Provide
from litestar.dto import DataclassDTO
from litestar.enums import RequestEncodingType
from litestar.exceptions import HTTPException
from litestar.openapi import ResponseSpec
from litestar.openapi.spec import Example
from litestar.params import Body
from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_429_TOO_MANY_REQUESTS,
)
from punq import Container

from app.api.exceptions.problem_details_dto import ProblemDetailsDTO
from app.api.exceptions.problem_factory import ErrorCodes
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
from app.core.errors.user import DeleteImageError, ImageUploadError
from app.core.errors.validation import (
    ImageExtensionValidationError,
    PasswordValidationError,
    UsernameValidationError,
)
from app.core.services.auth_service import AuthService
from app.core.services.user_service import UserService


@post(
    "/create",
    summary="Создание пользователя",
    description="Эндпоинт регистрации нового пользователя.",
    tags=["Пользователь"],
    status_code=HTTP_201_CREATED,
    dto=DataclassDTO[UserCreateDTO],
    return_dto=DataclassDTO[UserDTO],
    responses={
        HTTP_201_CREATED: ResponseSpec(
            description="Пользователь успешно создан",
            data_container=UserDTO,
        ),
        HTTP_400_BAD_REQUEST: ResponseSpec(
            description="Ошибка валидации данных",
            data_container=ProblemDetailsDTO,
            examples=[
                Example(
                    value=ErrorCodes.VALIDATION_ERROR.example(
                        "Email уже используется или данные невалидны"
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
async def create_user(
    data: UserCreateDTO,
    container: Container,
) -> UserDTO:
    """Запрос на создание нового пользователя."""
    user_service = container.resolve(UserService)

    user: User = await user_service.create_user(
        username=data.username,
        email=data.email,
        password=data.password,
        repeat_password=data.repeat_password,
    )

    user_dto = UserDTO.fromrow(user.__dict__)
    return user_dto.__dict__

@post(
    "/upload_image",
    summary="Загрузка изображения",
    description="Загрузка изображения текущего пользователя.",
    tags=["Пользователь"],
    status_code=HTTP_201_CREATED,
    return_dto=DataclassDTO[ImageDTO],
    dependencies={"current_user": Provide(AuthService.get_current_user)},
    responses={
        HTTP_201_CREATED: ResponseSpec(
            description="Изображение успешно загружено",
            data_container=ImageDTO,
        ),
        HTTP_400_BAD_REQUEST: ResponseSpec(
            description="Ошибка загрузки изображения",
            data_container=ProblemDetailsDTO,
            examples=[
                Example(
                    value=ErrorCodes.IMAGE_UPLOAD_ERROR.example(
                        "Недопустимое расширение файла или ошибка загрузки"
                    ),
                )
            ],
        ),
        HTTP_401_UNAUTHORIZED: ResponseSpec(
            description="Пользователь не авторизован",
            data_container=ProblemDetailsDTO,
            examples=[
                Example(
                    value=ErrorCodes.AUTHENTICATION_ERROR.example(
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
async def upload_image(
    container: Container,
    current_user: UserDTO,
    data: Annotated[UploadFile, Body(media_type=RequestEncodingType.MULTI_PART)],
) -> ImageDTO:
    """Запрос на загрузку изображения для текущего пользователя."""
    user_service = container.resolve(UserService)

    image: UploadedImage = await user_service.upload_image(
        user_id=current_user.id, file=data
    )

    image_dict = image.__dict__.copy()
    if "_id" in image_dict and isinstance(image_dict["_id"], ObjectId):
        image_dict["_id"] = str(image_dict["_id"])

    return ImageDTO.fromrow(image_dict)


@get(
    "/get_all_user_images",
    summary="Получение всех изображений пользователя",
    description="Возвращает список изображений текущего пользователя.",
    tags=["Пользователь"],
    status_code=HTTP_200_OK,
    return_dto=DataclassDTO[ImageDTO],
    dependencies={"current_user": Provide(AuthService.get_current_user)},
    responses={
        HTTP_200_OK: ResponseSpec(
            description="Список изображений пользователя",
            data_container=ImageDTO,
        ),
        HTTP_401_UNAUTHORIZED: ResponseSpec(
            description="Пользователь не авторизован",
            data_container=ProblemDetailsDTO,
            examples=[
                Example(
                    value=ErrorCodes.AUTHENTICATION_ERROR.example(
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
async def get_all_user_images(
    container: Container,
    current_user: UserDTO,
) -> list[ImageDTO]:
    """Запрос всех изображений текущего пользователя.

    Args:
        container (Container): Контейнер зависимостей для получения сервисов.
        current_user (UserDTO): Текущий авторизованный пользователь.

    Returns:
        list[ImageDTO]: Список DTO изображений пользователя.

    Raises:
        HTTPException: Если пользователь не авторизован.
    """
    user_service = container.resolve(UserService)

    images: list[UploadedImage] = await user_service.get_all_user_images(
        user_id=current_user.id
    )

    return [ImageDTO.fromrow(image.__dict__) for image in images]


@delete(
    "/delete_image",
    summary="Удаление изображения",
    description="Удаляет изображение текущего пользователя по URL.",
    tags=["Пользователь"],
    status_code=HTTP_200_OK,
    dependencies={"current_user": Provide(AuthService.get_current_user)},
    responses={
        HTTP_200_OK: ResponseSpec(
            description="Изображение успешно удалено",
            data_container=None,
        ),
        HTTP_400_BAD_REQUEST: ResponseSpec(
            description="Ошибка удаления изображения",
            data_container=ProblemDetailsDTO,
            examples=[
                Example(
                    value=ErrorCodes.IMAGE_DELETION_ERROR.example(
                        "Не удалось удалить изображение"
                    ),
                )
            ],
        ),
        HTTP_401_UNAUTHORIZED: ResponseSpec(
            description="Пользователь не авторизован",
            data_container=ProblemDetailsDTO,
            examples=[
                Example(
                    value=ErrorCodes.AUTHENTICATION_ERROR.example(
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
async def delete_image(
    container: Container,
    current_user: UserDTO | None,
    url: str,
) -> dict[str, str]:
    """Удаляет изображение текущего пользователя по URL.

    Args:
        container (Container): Контейнер зависимостей для получения сервисов.
        current_user (UserDTO | None): Текущий авторизованный пользователь или None, если не авторизован.
        url (str): URL изображения для удаления.

    Returns:
        dict[str, str]: Словарь с сообщением об успешном удалении.

    Raises:
        HTTPException: Если пользователь не авторизован или произошла ошибка удаления изображения.
    """
    user_service = container.resolve(UserService)

    await user_service.delete_image(user_id=current_user.id, url=url)
    return {"detail": "Изображение удалено"}


users_router = Router(
    path="/users",
    tags=["Пользователь"],
    route_handlers=[create_user, upload_image, get_all_user_images, delete_image],
)
