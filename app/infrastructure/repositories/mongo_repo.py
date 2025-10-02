from typing import Any, Generic, List, Tuple, Type, TypeVar
from uuid import uuid4

from pydantic import BaseModel

from app.infrastructure.gateways.mongo import MongoGateway


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

TDomain = TypeVar("TDomain")  # Объект бизнес логики (Domain Entity)
TDTO = TypeVar(
    "TDTO", bound=BaseModel
)  # DTO модель, создаваемая репозиторием на основе объекта бизнес логики (TDomain)


class MongoRepo(Generic[TDomain, TDTO]):
    """
    Универсальный репозиторий для MongoDB.

    Использует DTO (Pydantic) для валидации и сериализации,
    возвращает объекты Domain Entity.

    Args:
        gateway (MongoGateway): Гейтвей для доступа к MongoDB
        collection_name (str): Имя коллекции
        dto_model (Type[TDTO]): Pydantic-модель для валидации данных
        to_domain (Type[TDomain]): Конструктор для Domain Entity
    """

    def __init__(
        self,
        gateway: MongoGateway,
        collection_name: str,
        dto_model: Type[TDTO],
        to_domain: Type[TDomain],
    ) -> None:
        self._gw = gateway
        self.collection_name = collection_name
        self.dto_model = dto_model
        self.to_domain = to_domain

    async def get_one(self, query: dict[str, Any]) -> TDomain | None:
        cl = await self._gw.get_collection(self.collection_name)
        doc = await cl.find_one(query)
        if doc:
            dto = self.dto_model(**doc)
            return self.to_domain(
                _id=doc.get("_id"), **dto.model_dump(exclude_unset=True)  # type: ignore
            )
        return None

    async def get_all(self, query: dict[str, Any]) -> List[TDomain]:
        cl = await self._gw.get_collection(self.collection_name)
        cursor = cl.find(query)
        results = []
        async for doc in cursor:
            dto = self.dto_model(**doc)
            results.append(self.to_domain(**dto.model_dump()))
        return results

    async def add(self, data: dict[str, Any]) -> TDomain:
        """Добавляет новый документ в коллекцию."""
        cl = await self._gw.get_collection(self.collection_name)

        if "_id" not in data:
            data["_id"] = str(uuid4())

        dto = self.dto_model(**data)
        result = await cl.insert_one(dto.model_dump(exclude_unset=True))
        inserted_doc = await cl.find_one({"_id": result.inserted_id})
        return self.to_domain(**inserted_doc)

    async def get_or_create(self, entity: TDomain) -> Tuple[TDomain, bool]:
        cl = await self._gw.get_collection(self.collection_name)
        dto = self.dto_model(**entity.__dict__)
        result = await cl.update_one(
            dto.model_dump(exclude_unset=True),
            {"$setOnInsert": dto.model_dump(exclude_unset=True)},
            upsert=True,
        )
        created = result.upserted_id is not None
        fetched_doc = await cl.find_one(dto.model_dump(exclude_unset=True))
        fetched_dto = self.dto_model(**fetched_doc)
        return self.to_domain(**fetched_dto.model_dump()), created

    async def update(self, query: dict[str, Any], entity: TDomain) -> TDomain:
        cl = await self._gw.get_collection(self.collection_name)
        dto = self.dto_model(**entity.__dict__)
        filtered_data = {
            k: v for k, v in dto.model_dump().items() if v is not None
        }
        await cl.update_one(query, {"$set": filtered_data})
        updated_doc = await cl.find_one(query)
        if updated_doc is None:
            raise ValueError(f"No document found for query: {query}")
        updated_dto = self.dto_model(**updated_doc)
        return self.to_domain(**updated_dto.model_dump())

    async def delete(self, query: dict[str, Any]) -> bool:
        cl = await self._gw.get_collection(self.collection_name)
        result = await cl.find_one_and_delete(query)
        return result is not None
