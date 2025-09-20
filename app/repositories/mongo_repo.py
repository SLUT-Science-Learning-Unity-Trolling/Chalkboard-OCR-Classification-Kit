from typing import List, Optional, Tuple, Type

from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic import BaseModel

from app.repositories.__abc_repo__ import AbstractRepo


class MongoRepo(AbstractRepo):
    """
    Репозиторий для работы с MongoDB

    Info:
        collection - коллекция MongoDB
        model - Pydantic модель для валидации данных
    """

    collection: AsyncIOMotorCollection
    model: Type[BaseModel]

    def __init__(
        self, collection: AsyncIOMotorCollection, model: Type[BaseModel]
    ):
        self.collection = collection
        self.model = model

    async def find_one(self, **kwargs) -> Optional[BaseModel]:
        document = await self.collection.find_one(kwargs)
        return self.model(**document) if document else None

    async def find_all(self, **kwargs) -> List[BaseModel]:
        documents = await self.collection.find(kwargs).to_list(None)
        return [self.model(**doc) for doc in documents]

    async def create_some(self, **kwargs) -> BaseModel:
        validated_data = self.model(**kwargs).model_dump(exclude_unset=True)
        result = await self.collection.insert_one(validated_data)
        document = await self.collection.find_one({"_id": result.inserted_id})
        return self.model(**document)

    async def get_or_create(self, **kwargs) -> Tuple[BaseModel, bool]:
        validated_data = self.model(**kwargs).model_dump(exclude_unset=True)
        document = await self.collection.find_one(kwargs)
        if document:
            return self.model(**document), False
        result = await self.collection.insert_one(validated_data)
        document = await self.collection.find_one({"_id": result.inserted_id})
        return self.model(**document), True

    async def update(self, obj: BaseModel, **kwargs) -> BaseModel:
        update_data = {k: v for k, v in kwargs.items() if v is not None}
        await self.collection.update_one(
            {"_id": obj.model_dump().get("_id")}, {"$set": update_data}
        )
        updated_document = await self.collection.find_one(
            {"_id": obj.model_dump().get("_id")}
        )
        return self.model(**updated_document)
