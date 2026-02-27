"""Модуль содержит класс UserService для работы с пользователями."""
# UserService

import io

from time import time
from typing import Any
from uuid import uuid4

from bson import ObjectId
from litestar.datastructures import UploadFile

from app.adapters.gateways.s3 import MinioGateway
from app.adapters.repositories.abc_repo import RepositoryInterface
from app.core.domain.models.image import UploadedImage
from app.core.domain.models.user import User
from app.core.errors.auth import (
    EmailAlreadyTakenError,
    PasswordDontMatchError,
    UsernameAlreadyTakenError,
)
from app.core.errors.user import (
    AbsentUserError,
    DeleteImageError,
    GetImagesError,
    ImageUploadError,
    UserCreationError,
)
from app.core.errors.validation import (
    ImageNotFoundError,
)
from app.core.services.security_service import SecurityService
from app.core.services.validation_service import ImageValidator, ValidationService


class UserService:
    """Сервис для работы с пользователями."""

    def __init__(
        self,
        user_repo: RepositoryInterface,
        image_repo: RepositoryInterface,
        security: SecurityService,
        validator: ValidationService,
        image_validator: ImageValidator,
        storage: MinioGateway,
    ) -> None:
        """Конструктор.

        Args:
            user_repo (RepositoryInterface): Репозиторий пользователей
            image_repo (RepositoryInterface): Репозиторий изображений
            security (SecurityService): Секьюрити сервис
            validator (ValidationService): Сервис валидации
            image_validator (ImageValidator): Сервис валидации изображений
            storage (MinioGateway): Сервис хранилища
        """
        self._user_repo = user_repo
        self._image_repo = image_repo
        self._security = security
        self._validator = validator
        self._image_validator = image_validator
        self._storage = storage

    async def create_user(
        self, username: str, email: str, password: str, repeat_password: str
    ) -> User:
        """Создает нового пользователя.

        Проверяет корректность пароля, уникальность имени пользователя и email,
        валидирует email и создает хэш пароля.

        Args:
            username (str): Имя пользователя.
            email (str): Email пользователя.
            password (str): Пароль пользователя.
            repeat_password (str): Подтверждение пароля.

        Returns:
            User: Экземпляр созданного пользователя.

        Raises:
            PasswordDontMatchError: Если пароли не совпадают.
            UsernameAlreadyTaken: Если имя пользователя уже занято.
            EmailAlreadyTakenError: Если email уже используется.
            UserCreationError: Если произошла ошибка на сервере.
        """
        if password != repeat_password:
            raise PasswordDontMatchError("Пароли не совпадают")

        self._validator.validate_password(password)
        self._validator.validate_username(username)

        existing_user = await self.does_user_exists(username, email)
        if existing_user:
            if existing_user.get("username") == username:
                raise UsernameAlreadyTakenError("Имя пользователя уже занято")
            if existing_user.get("email") == email.lower():
                raise EmailAlreadyTakenError("Почта уже занята")

        self._validator.validate_email(email)

        salt, _hash = self._security.hash_password(password)
        password_hash = self._security.serialize_hash(salt, _hash)

        user_data = {
            "username": username,
            "email": email.lower(),
            "password_hash": password_hash,
        }
        try:
            id = await self._user_repo.add(user_data)

        except Exception:
            raise UserCreationError("Произошла ошибка") from None

        user = await self._user_repo.get_one({"_id": id})

        return User(**user)

    async def get_user_by_id(self, user_id: str) -> dict[str, Any]:
        """Возвращает пользователя по ID.

        Args:
            user_id (str): ID пользователя

        Returns:
            dict[str, Any]: Пользователь
        """
        user = await self._user_repo.get_one({"_id": ObjectId(user_id)})
        return user

    async def does_user_exists(
        self, username: str, email: str
    ) -> dict[str, Any] | None:
        """Проверяет, существует ли пользователь по username или email.

        Args:
            username (str): Имя пользователя
            email (str): Email пользователя

        Returns:
            dict[str, Any] | None: Пользователь или None
        """
        user = await self._user_repo.get_one({"username": username})
        if user:
            return user

        user = await self._user_repo.get_one({"email": email.lower()})
        return user

    async def upload_image(self, user_id: str, file: UploadFile) -> UploadedImage:
        """Загружает локальное изображение пользователя.

        Args:
            user_id: ID пользователя
            file: Локальный файл (UploadFile)

        Returns:
            UploadedImage: Загруженное изображение
        """
        self._image_validator.validate_image_file(file)

        content = await file.read()
        raw_image = io.BytesIO(content)
        raw_img_size = len(content)
        filename = file.filename

        unique_filename = f"{uuid4()}_{filename}"
        try:
            self._storage.put_object(
                object_name=unique_filename, data=raw_image, size=raw_img_size
            )
        except Exception:
            raise ImageUploadError(
                "Произошла ошибка при загрузке изображения",
            ) from None

        endpoint = self._storage._client.meta.endpoint_url.rstrip("/")
        url = f"{endpoint}/{self._storage._bucket}/{unique_filename}"

        image_data = {
            "_user_id": ObjectId(user_id),
            "url": url,
            "uploaded_at": int(time()),
        }

        try:
            id = await self._image_repo.add(image_data)
            image = await self._image_repo.get_one({"_id": id})

        except Exception:
            raise ImageUploadError(
                "Произошла ошибка при загрузке изображения"
            ) from None

        return UploadedImage(**image)

    async def get_all_user_images(self, user_id: str) -> list[UploadedImage]:
        """Возвращает все изображения пользователя.

        Args:
            user_id (str): Уникальный идентификатор пользователя

        Returns:
            list[UploadedImage]: Список изображений пользователя
        """
        try:
            images = await self._image_repo.get_many(
                {"_user_id": ObjectId(user_id)}, limit=30
            )

        except GetImagesError:
            raise GetImagesError("Произошла ошибка при получении картинок") from None

        return [UploadedImage(**image) for image in images]

    async def delete_image(self, url: str, user_id: str) -> None:
        """Удаляет изображение пользователя.

        Args:
            url (str): Путь к изображению
            user_id (str): Уникальный идентификатор пользователя
        """
        user = await self._user_repo.get_one({"_id": ObjectId(user_id)})
        if not user:
            raise AbsentUserError("Пользователь не найден")

        image = await self._image_repo.get_one({"url": url})
        if not image:
            raise ImageNotFoundError("Картинка не найдена")

        if user.get("_id") != image.get("_user_id"):
            raise DeleteImageError("Нельзя удалить картинку чужого пользователя")

        try:
            await self._image_repo.delete({"url": url})
        except Exception:
            raise DeleteImageError("Произошла ошибка при удалении картинки") from None

        try:
            self._storage.delete_file(url.split("/")[-1])
        except Exception:
            raise DeleteImageError("Произошла ошибка при удалении картинки") from None
