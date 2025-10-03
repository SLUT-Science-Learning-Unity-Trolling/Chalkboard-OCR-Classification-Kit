from typing import Any
from app.core.services.security_service import SecurityService
from app.errors.auth import InvalidEmailOrPassword
from app.infrastructure.repositories.__abc_repo__ import RepositoryInterface


class AuthService:
    """Сервис для аутентификации пользователей."""

    def __init__(
        self, repository: RepositoryInterface, security: SecurityService
    ):
        """Конструктор.

        Args:
            repository (RepositoryInterface): Репозиторий
            security (SecurityService): Секьюрити сервис
        """
        self._repo = repository
        self._security = security
        pass

    async def auth_existing_user(
        self, email: str, password: str
    ) -> dict[str, Any]:
        """Аутентификация существующего пользователя."""
        user = await self._repo.get_one({"email": email})
        if not user:
            raise InvalidEmailOrPassword

        hash, salt = self._security.deserialize_hash(user["password_hash"])
        user["hash"] = hash
        user["salt"] = salt

        if self._security.verify_hash(
            password=password, salt=user["salt"], hash_=user["hash"]
        ):
            return user

        else:
            raise InvalidEmailOrPassword
