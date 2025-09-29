from app.core.models.user import User
from app.errors.user import UserCreationError
from app.infrastructure.repositories.__abc_repo__ import RepositoryInterface


class UserService:
    def __init__(self, repository: RepositoryInterface) -> None:
        self._repo = repository

    async def create_user(self, username: str, email: str) -> User:
        """
        Создает нового пользователя.

        Args:
            username: Имя пользователя
            email: Email пользователя

        Returns:
            User: Созданный пользователь

        Raises:
            ValueError: Если пользователь не был создан
        """

        user_data = {"username": username, "email": email}

        user = await self._repo.add(user_data)

        if user is None:
            raise UserCreationError(f"Failed to create user with email={email}")

        return user
