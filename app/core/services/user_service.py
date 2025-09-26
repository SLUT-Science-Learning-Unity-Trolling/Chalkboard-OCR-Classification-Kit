from app.core.models.user import User
from app.infrastructure.repositories.__abc_repo__ import RepositoryInterface


class UserService:
    def __init__(self, repository: RepositoryInterface) -> None:
        self._repo = repository

    async def create_user(self, username: str, email: str) -> User:
        await self._repo.add({"username": username, "email": email})

        user = await self._repo.get_one({"email": email})
        if user is None:
            raise ValueError(
                f"User with email={email} not found after creation"
            )

        user_model = User(
            id=user["_id"],
            username=user["username"],
            email=user["email"],
        )
        return user_model
