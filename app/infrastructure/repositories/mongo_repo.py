from typing import Any, List, Tuple, Type, TypeVar

from pydantic import BaseModel

from app.infrastructure.gateways.mongo import MongoGateway
from app.infrastructure.repositories.__abc_repo__ import RepositoryInterface


T = TypeVar("T", bound=BaseModel)


class MongoRepo(RepositoryInterface):
    """Реализация репозитория для работы с MongoDB

    Использует библиотеку pymongo для синхронного взаимодействия с MongoDB через MongoGateway.
    Pydantic нужен для строгой валидации данных.

    Args:
        gateway (MongoGateway): Гейтвей для доступа к MongoDB.
        collection_name (str): Имя коллекции.
        model (Type[BaseModel]): Pydantic-модель для валидации данных.
    """

    def __init__(
        self,
        gateway: MongoGateway,
        collection_name: str,
        model: Type[T],
    ) -> None:
        self._gw = gateway
        self.collection_name = collection_name
        self.model = model

    async def get_one(self, query: dict[str, Any]) -> T | None:
        cl = self._gw.get_collection(self.collection_name)
        document = await cl.find_one(query)
        return self.model(**document) if document else None

    async def get_all(self, query: dict[str, Any]) -> List[T]:
        cl = self._gw.get_collection(self.collection_name)
        cursor = cl.find(query)
        documents = [self.model(**doc) async for doc in cursor]
        return documents

    async def add(self, document: dict[str, Any]) -> T:
        cl = self._gw.get_collection(self.collection_name)
        validated_data = self.model(**document).model_dump(exclude_unset=True)
        result = await cl.insert_one(validated_data)
        fetched_document = await cl.find_one({"_id": result.inserted_id})
        return self.model(**fetched_document)

    async def get_or_create(self, document: dict[str, Any]) -> Tuple[T, bool]:
        cl = self._gw.get_collection(self.collection_name)
        validated_data = self.model(**document).model_dump(exclude_unset=True)

        result = await cl.update_one(
            validated_data, {"$setOnInsert": validated_data}, upsert=True
        )

        created = result.upserted_id is not None
        fetched_document = await cl.find_one(validated_data)
        return self.model(**fetched_document), created

    async def update(
        self, query: dict[str, Any], update_data: dict[str, Any]
    ) -> T:
        cl = self._gw.get_collection(self.collection_name)
        filtered_update_data = {
            k: v for k, v in update_data.items() if v is not None
        }
        await cl.update_one(query, {"$set": filtered_update_data})
        updated_document = await cl.find_one(query)
        return self.model(**updated_document)
