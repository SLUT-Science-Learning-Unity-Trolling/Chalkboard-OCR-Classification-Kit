from abc import ABC, abstractmethod
from typing import Any, Generic, List, Tuple, TypeVar

from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)


class RepositoryInterface(ABC, Generic[T]):
    """Абстрактный generic-интерфейс для репозиториев.

    Все методы должны быть реализованы в классах-наследниках.
    """

    @abstractmethod
    async def get_one(self, query: dict[str, Any]) -> T | None:
        """Ищет и возвращает один объект по заданному запросу."""
        raise NotImplementedError

    @abstractmethod
    async def get_all(self, query: dict[str, Any]) -> List[T]:
        """Возвращает список всех объектов, соответствующих запросу."""
        raise NotImplementedError

    @abstractmethod
    async def add(self, document: dict[str, Any]) -> T:
        """Создаёт новый объект в хранилище."""
        raise NotImplementedError

    @abstractmethod
    async def get_or_create(self, document: dict[str, Any]) -> Tuple[T, bool]:
        """Ищет объект по критериям или создаёт новый.

        Возвращает кортеж (объект, создан ли новый).
        """
        raise NotImplementedError

    @abstractmethod
    async def update(
        self, query: dict[str, Any], update_data: dict[str, Any]
    ) -> T:
        """Обновляет существующий объект по заданному запросу."""
        raise NotImplementedError
