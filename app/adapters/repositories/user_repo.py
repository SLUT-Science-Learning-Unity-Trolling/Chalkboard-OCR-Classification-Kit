"""Модуль содержит класс UserRepo для работы с базой данных MongoDB."""
# UserRepo

from app.adapters.interfaces.db import DBGatewayInterface
from app.adapters.repositories.mongo_repo import MongoRepo


class UserRepo(MongoRepo):
    """Репозиторий для работы с пользователями."""

    def __init__(self, gateway: DBGatewayInterface) -> None:
        """Инициализация репозитория.

        Args:
            gateway (DBGatewayInterface): гейтвей для работы с базой данных.
        """
        super().__init__(gateway, collection_name="users")
