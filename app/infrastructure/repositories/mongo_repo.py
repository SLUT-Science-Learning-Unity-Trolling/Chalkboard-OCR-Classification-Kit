from typing import Any

from bson import ObjectId
from pymongo.asynchronous.collection import AsyncCollection

from app.infrastructure.interfaces.db import DBGatewayInterface
from app.infrastructure.repositories.__abc_repo__ import RepositoryInterface


"""
Цикл жизни (Для понимания как это работает):
    1. Клиент -> JSON: Клиент отправляет данные в формате JSON через HTTP-запрос.
    2. API -> DTO: API (FastAPI) валидирует JSON с помощью Pydantic и создаёт DTO.
    3. Сервис -> DE: Сервисный слой преобразует DTO в Domain Entity и выполняет бизнес-логику.

    4. Репозиторий -> ODM -> База:
        Репозиторий преобразует DE в ODM-модель (или напрямую использует DE, если ODM поддерживает).
        ODM валидирует и сохраняет данные в MongoDB.

    5. Чтение из базы ->→ DE:
        Репозиторий через ODM извлекает документ из MongoDB.
        ODM преобразует документ в ODM-модель.
        Репозиторий конвертирует ODM-модель в DE.

    6. Сервис -> API: Сервис возвращает DE после выполнения бизнес-логики.
    7. API -> DTO -> JSON -> Клиент: API преобразует DE в DTO (Pydantic-модель), сериализует его в JSON и отправляет клиенту.
"""


class MongoRepo(RepositoryInterface):
    """Репозиторий для работы с mongodb."""

    def __init__(
        self, gateway: DBGatewayInterface, collection_name: str
    ) -> None:
        """Конструктор.

        Args:
            gateway (DBGatewayInterface): Гейт подключения к бд
            collection_name (str): Имя коллекции
        """
        self.__gw = gateway
        self.collection_name = collection_name

    async def _init_collection(self) -> AsyncCollection:
        return await self.__gw.get_collection(self.collection_name)  # type: ignore

    async def add(self, data: dict[str, Any]) -> ObjectId:
        """Добавление документа в БД.

        Args:
            data (dict[str, Any]): Документ

        Returns:
            ObjectId: ID нового документа
        """
        collection = await self._init_collection()
        result = await collection.insert_one(data)
        return result.inserted_id

    async def get_one(self, query: dict[str, Any]) -> dict[str, Any]:
        """Получение конкретного объекта из БД.

        Args:
            query (dict[str, Any]): Поисковый запрос

        Returns:
            dict[str, Any]: Результат поиска
        """
        collection = await self._init_collection()
        result = await collection.find_one(query)
        return result

    async def get_many(
        self, query: dict[str, Any], limit: int = 10
    ) -> list[dict[str, Any]]:
        """Получение N объектов из БД.

        Args:
            query (dit[str, Any]): Поисковый запрос
            limit (int): Кол-во объектов

        Returns:
            list[dict[str, Any]]: Результат поиска
        """
        collection = await self._init_collection()
        result = collection.find(query).limit(limit)
        return await result.to_list()

    async def update(
        self, query: dict[str, Any], update_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Обновление документа.

        Args:
            query (dict[str, Any]): Поисковый запрос
            update_data (dict[str, Any]): Данные для обновления

        Returns:
            dict[str, Any]: Обновленный документ
        """
        collection = await self._init_collection()
        result = await collection.find_one_and_update(
            filter=query, update=update_data
        )
        return result

    async def delete(self, query: dict[str, Any]) -> bool:
        """Удаление объекта.

        Args:
            query (dict[str, Any]): Поисковый запрос

        Returns:
            bool: Результат операции

        Raises:
            ValueError: При неудачной операции
        """
        try:
            collection = await self._init_collection()
            await collection.find_one_and_delete(query)
            return True
        except Exception as e:
            raise ValueError(e)
