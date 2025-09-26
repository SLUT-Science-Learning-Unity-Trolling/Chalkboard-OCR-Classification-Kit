from abc import ABC, abstractmethod
from typing import Any, Generic, List, Tuple, TypeVar


T = TypeVar("T")


class RepositoryInterface(ABC, Generic[T]):
    """Абстрактный generic-интерфейс для репозиториев."""

    @abstractmethod
    async def get_one(self, query: dict[str, Any]) -> T | None:
        """Ищет и возвращает один объект по заданному запросу."""
        raise NotImplementedError

    @abstractmethod
    async def get_all(self, query: dict[str, Any]) -> List[T]:
        """Возвращает список всех объектов, соответствующих запросу."""
        raise NotImplementedError

    @abstractmethod
    async def add(self, entity: T) -> T:
        """Создаёт новый объект в хранилище."""
        raise NotImplementedError

    @abstractmethod
    async def get_or_create(self, entity: T) -> Tuple[T, bool]:
        """Ищет объект по критериям или создаёт новый.

        Возвращает кортеж (объект, создан ли новый).
        """
        raise NotImplementedError

    @abstractmethod
    async def update(self, query: dict[str, Any], entity: T) -> T:
        """Обновляет существующий объект по заданному запросу."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, query: dict[str, Any]) -> bool:
        """Удаляет объект по заданному запросу."""
        raise NotImplementedError
