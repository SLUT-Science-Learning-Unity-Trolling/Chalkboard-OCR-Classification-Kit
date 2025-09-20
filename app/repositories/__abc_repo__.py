from abc import ABC, abstractmethod
from typing import Any, List, Optional, Tuple


class RepositoryInterface(ABC):
    """Абстрактный интерфейс для репозиториев в проекте Chalkboard OCR Classification Kit.

    Определяет контракт для работы с данными в хранилище. Все методы должны быть реализованы
    в классах-наследниках. Прямое использование интерфейса невозможно из-за NotImplementedError.

    Raises:
        NotImplementedError: Если метод вызывается напрямую.
    """

    @abstractmethod
    async def get_one(self, query: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Ищет и возвращает один документ по заданному запросу."""
        raise NotImplementedError

    @abstractmethod
    async def get_all(self, query: dict[str, Any]) -> List[dict[str, Any]]:
        """Возвращает список всех документов, соответствующих запросу."""
        raise NotImplementedError

    @abstractmethod
    async def add(self, document: dict[str, Any]) -> dict[str, Any]:
        """Создаёт новый документ в хранилище."""
        raise NotImplementedError

    @abstractmethod
    async def get_or_create(
        self, document: dict[str, Any]
    ) -> Tuple[dict[str, Any], bool]:
        """Ищет документ по критериям или создаёт новый."""
        raise NotImplementedError

    @abstractmethod
    async def update(
        self, query: dict[str, Any], update_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Обновляет существующий документ по заданному запросу."""
        raise NotImplementedError
