"""Модуль содержит абстрактный репозиторий для работы с БД."""

# RepositoryInterface
from abc import ABC, abstractmethod
from typing import Any

from app.adapters.interfaces.db import DBGatewayInterface


class RepositoryInterface(ABC):
    """Базовый репозиторий для работы с с БД."""

    def __init__(self, gateway: DBGatewayInterface) -> None:
        """Конструктор.

        Args:
            gateway (DBGateway): Гейт к бд.
        """
        self.__gw = gateway

    @abstractmethod
    async def add(self, data: dict[str, Any]) -> Any:
        """Добавление нового документа/таблицы.

        Returns:
            Any: ID нового объекта
        """
        raise NotImplementedError

    @abstractmethod
    async def get_one(self, query: dict[str, Any]) -> dict[str, Any]:
        """Получение одного объекта."""
        raise NotImplementedError

    @abstractmethod
    async def get_many(self, query: dict[str, Any], limit: int) -> list[dict[str, Any]]:
        """Получение нескольких объектов.

        Args:
            query (dict[str, Any]): Поисковый запрос
            limit (int): Кол-во объектов

        Returns:
            list[dict[str, Any]]: Результат поиска
        """
        raise NotImplementedError

    @abstractmethod
    async def update(
        self, query: dict[str, Any], update_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Обновление объекта.

        Args:
            query (dict[str, Any]): Поисковый запрос
            update_data (dict[str, Any]): Данные для обновления

        Returns:
            dict[str, Any]: Обновленный объект
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(self, query: dict[str, Any]) -> bool:
        """Удаление объекта.

        Args:
            query (dict[str, Any]): Поисковый запрос

        Returns:
            bool: Результат операции
        """
        raise NotImplementedError
