"""Модуль содержит класс MongoRepo для работы с базой данных MongoDB."""
# MongoRepo

from typing import Any

from bson import ObjectId
from pymongo.asynchronous.collection import AsyncCollection

from app.adapters.interfaces.db import DBGatewayInterface
from app.adapters.repositories.abc_repo import RepositoryInterface


"""
Цикл жизни (Для понимания как это работает):
    1. Клиент -> JSON: Клиент отправляет данные в формате JSON через HTTP-запрос.
    2. API -> DTO: API (FastAPI) валидирует JSON и создаёт DTO.
    3. Сервис -> DE: Сервисный слой преобразует DTO в Domain Entity и выполняет бизнес-логику.

    4. Репозиторий -> ODM -> База:
        Репозиторий преобразует DE в ODM-модель (или напрямую использует DE, если ODM поддерживает).
        ODM валидирует и сохраняет данные в MongoDB.

    5. Чтение из базы ->→ DE:
        Репозиторий через ODM извлекает документ из MongoDB.
        ODM преобразует документ в ODM-модель.
        Репозиторий конвертирует ODM-модель в DE.

    6. Сервис -> API: Сервис возвращает DE после выполнения бизнес-логики.
    7. API -> DTO -> JSON -> Клиент: API преобразует DE в DTO, сериализует его в JSON и отправляет клиенту.
"""


class MongoRepo(RepositoryInterface):
    """Асинхронный репозиторий для работы с MongoDB.

    Репозиторий инкапсулирует работу с коллекцией MongoDB, предоставляя
    CRUD операции для работы с документами.
    """

    def __init__(self, gateway: DBGatewayInterface, collection_name: str) -> None:
        """Инициализация репозитория.

        Args:
            gateway (DBGatewayInterface): Объект для работы с базой данных.
            collection_name (str): Название коллекции MongoDB.
        """
        self.__gw = gateway
        self.collection_name = collection_name

    async def _init_collection(self) -> AsyncCollection:
        """Получение асинхронного объекта коллекции.

        Returns:
            AsyncCollection: Асинхронная коллекция MongoDB.
        """
        return await self.__gw.get_collection(self.collection_name)  # type: ignore

    async def add(self, data: dict[str, Any]) -> ObjectId:
        """Добавляет новый документ в коллекцию.

        Args:
            data (dict[str, Any]): Словарь с данными документа.

        Returns:
            ObjectId: Уникальный идентификатор добавленного документа.
        """
        collection = await self._init_collection()
        result = await collection.insert_one(data)
        return result.inserted_id

    async def get_one(self, query: dict[str, Any]) -> dict[str, Any]:
        """Получает один документ из коллекции по условию.

        Args:
            query (dict[str, Any]): Словарь с фильтром поиска.

        Returns:
            dict[str, Any] | None: Найденный документ или None, если не найден.
        """
        collection = await self._init_collection()
        result = await collection.find_one(query)
        return result

    async def get_many(
        self, query: dict[str, Any], limit: int = 1000
    ) -> list[dict[str, Any]]:
        """Получает несколько документов из коллекции.

        Args:
            query (dict[str, Any]): Словарь с фильтром поиска.
            limit (int, optional): Максимальное количество документов. По умолчанию 10.

        Returns:
            list[dict[str, Any]]: Список найденных документов.
        """
        collection = await self._init_collection()
        result = collection.find(query).limit(limit)
        return await result.to_list()

    async def update(
        self, query: dict[str, Any], update_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Обновляет один документ в коллекции.

        Args:
            query (dict[str, Any]): Словарь с фильтром поиска документа.
            update_data (dict[str, Any]): Данные для обновления (например, {"$set": {...}}).

        Returns:
            dict[str, Any] | None: Обновленный документ или None, если документ не найден.
        """
        collection = await self._init_collection()
        result = await collection.find_one_and_update(filter=query, update=update_data)
        return result

    async def delete(self, query: dict[str, Any]) -> bool:
        """Удаляет один документ из коллекции.

        Args:
            query (dict[str, Any]): Словарь с фильтром для удаления.

        Returns:
            bool: True, если документ был успешно удален, иначе False.

        Raises:
            ValueError: Если возникла ошибка при удалении документа.
        """
        try:
            collection = await self._init_collection()
            await collection.find_one_and_delete(query)
            return True
        except Exception as e:
            raise ValueError(f"Ошибка при удалении документа: {e}") from e
