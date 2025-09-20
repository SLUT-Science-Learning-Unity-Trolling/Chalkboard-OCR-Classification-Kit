from typing import Any, List, Optional, Tuple, Type

from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic import BaseModel

from app.infrastructure.repositories.__abc_repo__ import RepositoryInterface


class MongoRepo(RepositoryInterface):
    """Реализация репозитория для работы с MongoDB в проекте Chalkboard OCR Classification Kit.

    Использует библиотеку motor для асинхронного взаимодействия с MongoDB и Pydantic для валидации данных.

    Args:
        collection (AsyncIOMotorCollection): Коллекция MongoDB для работы.
        model (Type[BaseModel]): Pydantic-модель для валидации данных.
    """

    def __init__(
        self, collection: AsyncIOMotorCollection, model: Type[BaseModel]
    ):
        self.collection = collection
        self.model = model

    async def get_one(self, query: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Ищет и возвращает один документ по заданному запросу.

        Args:
            query (dict[str, Any]): Фильтр для поиска (например, {"id": "123"}).

        Returns:
            Optional[dict[str, Any]]: Экземпляр Pydantic-модели или None, если документ не найден.
        """
        document = await self.collection.find_one(query)
        return self.model(**document).model_dump() if document else None

    async def get_all(self, query: dict[str, Any]) -> List[dict[str, Any]]:
        """Возвращает список всех документов, соответствующих запросу.

        Args:
            query (dict[str, Any]): Фильтр для поиска (опционально).

        Returns:
            List[dict[str, Any]]: Список экземпляров Pydantic-модели.
        """
        documents = await self.collection.find(query).to_list(None)
        return [self.model(**doc).model_dump() for doc in documents]

    async def add(self, document: dict[str, Any]) -> dict[str, Any]:
        """Создаёт новый документ в коллекции.

        Args:
            document (dict[str, Any]): Данные для создания документа.

        Returns:
            dict[str, Any]: Созданный экземпляр Pydantic-модели.
        """
        validated_data = self.model(**document).model_dump(exclude_unset=True)
        result = await self.collection.insert_one(validated_data)
        document = await self.collection.find_one({"_id": result.inserted_id})
        return self.model(**document).model_dump()

    async def get_or_create(
        self, document: dict[str, Any]
    ) -> Tuple[dict[str, Any], bool]:
        """Ищет документ по критериям или создаёт новый.

        Args:
            document (dict[str, Any]): Данные для поиска или создания.

        Returns:
            Tuple[dict[str, Any], bool]: Кортеж из экземпляра Pydantic-модели и флага (True, если создан; False, если найден).
        """
        validated_data = self.model(**document).model_dump(exclude_unset=True)
        existing = await self.collection.find_one(validated_data)
        if existing:
            return self.model(**existing).model_dump(), False
        result = await self.collection.insert_one(validated_data)
        document = await self.collection.find_one({"_id": result.inserted_id})
        return self.model(**document).model_dump(), True

    async def update(
        self, query: dict[str, Any], update_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Обновляет существующий документ по заданному запросу.

        Args:
            query (dict[str, Any]): Фильтр для поиска документа.
            update_data (dict[str, Any]): Данные для обновления.

        Returns:
            dict[str, Any]: Обновлённый экземпляр Pydantic-модели.
        """
        update_data = {k: v for k, v in update_data.items() if v is not None}
        await self.collection.update_one(query, {"$set": update_data})
        updated_document = await self.collection.find_one(query)
        return self.model(**updated_document).model_dump()
