"""Модуль содержит класс ImageRepo для работы с базой данных MongoDB."""
# ImageRepo

from app.adapters.interfaces.db import DBGatewayInterface
from app.adapters.repositories.mongo_repo import MongoRepo


class ImageRepo(MongoRepo):
    """Класс для работы с базой данных MongoDB."""

    def __init__(self, gateway: DBGatewayInterface) -> None:
        """Инициализация репозитория.

        Args:
            gateway (DBGatewayInterface): гейтвей для работы с базой данных.
        """
        super().__init__(gateway, collection_name="images")
