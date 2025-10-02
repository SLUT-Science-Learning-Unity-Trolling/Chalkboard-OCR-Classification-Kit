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
    def __init__(
        self, repository: RepositoryInterface, security: SecurityService
    ) -> None:
        self._repo = repository
        self._security = security

    async def create_user(
        self, username: str, email: str, password: str, repeat_password: str
    ) -> User:
        """Create a new user.
        Создает нового пользователя.

        Args:
            username: The username of the new user.
            email: The email address of the new user.
            password: The password of the new user.
            username: Имя пользователя
            email: Email пользователя

        Returns:
            User: The created user.
            User: Созданный пользователь

        Raises:
            UserCreationError: If the user could not be created.
            ValueError: Если пользователь не был создан
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
            raise EmailValidationError

        salt, _hash = self._security.hash_password(password)
        password_hash = self._security.serialize_hash(salt, _hash)

        user_data = {
            "username": username,
            "email": email,
            "password_hash": password_hash,
        }
        try:
            user = await self._repo.add(user_data)
        except Exception:
            raise UserCreationError("Произошла ошибка")

        return user
