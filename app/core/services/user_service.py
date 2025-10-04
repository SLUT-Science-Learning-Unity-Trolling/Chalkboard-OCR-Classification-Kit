from typing import Any
from bson import ObjectId
from email_validator import EmailNotValidError, validate_email

from app import config
from app.core.models.user import User
from app.core.services.security_service import SecurityService
from app.errors.auth import (
    EmailAlreadyTaken,
    EmailValidationError,
    PasswordDontMatch,
)
from app.errors.security import PasswordValidationError
from app.errors.user import UserCreationError
from app.infrastructure.repositories.__abc_repo__ import RepositoryInterface


class UserService:
    """Сервис для работы с пользователями."""

    def __init__(
        self, repository: RepositoryInterface, security: SecurityService
    ) -> None:
        """Конструктор.

        Args:
            repository (RepositoryInterface): Репозиторий
            security (SecurityService): Секьюрити сервис
        """
        self._repo = repository
        self._security = security

    async def create_user(
        self, username: str, email: str, password: str, repeat_password: str
    ) -> User:
        """Создает нового пользователя.

        Args:
            username: Имя пользователя
            email: Email пользователя
            password: Пароль пользователя
            repeat_password: Повтор пароля пользователя

        Returns:
            User: Созданный пользователь

        Raises:
            UserCreationError: Если пользователь не был создан
        """
        if password != repeat_password:
            raise PasswordDontMatch

        if not await self._security.validate_password(password):
            raise PasswordValidationError

        if await self._repo.get_one({"email": email}):
            raise EmailAlreadyTaken

        try:
            validate_email(email, test_environment=config.Config.DEBUG)
        except EmailNotValidError:
            raise EmailValidationError("Введите корректный email")

        salt, _hash = self._security.hash_password(password)
        password_hash = self._security.serialize_hash(salt, _hash)

        user_data = {
            "username": username,
            "email": email.lower(),
            "password_hash": password_hash,
        }
        try:
            id = await self._repo.add(user_data)

        except Exception:
            raise UserCreationError("Произошла ошибка")

        user = await self._repo.get_one({"_id": id})

        return User(**user)

    async def get_user_by_id(self, user_id: str) -> dict[str, Any]:
        """Возвращает пользователя по ID."""
        user = await self._repo.get_one({"_id": ObjectId(user_id)})
        return user
