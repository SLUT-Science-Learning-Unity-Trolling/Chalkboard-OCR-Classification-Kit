from typing import Any
from bson import ObjectId
from email_validator import EmailNotValidError, validate_email

from app import config
from app.core.domain.models.user import User
from app.core.services.security_service import SecurityService
from app.core.errors.auth import (
    EmailAlreadyTaken,
    EmailValidationError,
    PasswordDontMatch,
    UsernameAlreadyTaken,
)
from app.core.errors.validation import (
    PasswordValidationError,
    UsernameValidationError,
)
from app.core.errors.user import UserCreationError
from app.adapters.repositories.abc_repo import RepositoryInterface
from app.core.services.validation_service import ValidationService


class UserService:
    """Сервис для работы с пользователями."""

    def __init__(
        self,
        repository: RepositoryInterface,
        security: SecurityService,
        validator: ValidationService,
    ) -> None:
        """Конструктор.

        Args:
            repository (RepositoryInterface): Репозиторий
            security (SecurityService): Секьюрити сервис
            validator (ValidationService): Сервис валидации
        """
        self._repo = repository
        self._security = security
        self._validator = validator

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

        if not await self._validator.validate_password(password):
            raise PasswordValidationError

        if not await self._validator.validate_username(username):
            raise UsernameValidationError

        existing_user = await self.does_user_exists(username, email)
        if existing_user:
            if existing_user.get("username") == username:
                raise UsernameAlreadyTaken
            if existing_user.get("email") == email.lower():
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
        """Возвращает пользователя по ID.

        Args:
            user_id (str): ID пользователя

        Returns:
            dict[str, Any]: Пользователь
        """
        user = await self._repo.get_one({"_id": ObjectId(user_id)})
        return user

    async def does_user_exists(
        self, username: str, email: str
    ) -> dict[str, Any] | None:
        """Проверяет, существует ли пользователь по username или email.

        Args:
            username (str): Имя пользователя
            email (str): Email пользователя

        Returns:
            dict[str, Any]: Пользователь
        """
        user = await self._repo.get_one({"username": username})
        if user:
            return user

        user = await self._repo.get_one({"email": email.lower()})
        return user
