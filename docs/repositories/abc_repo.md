# RepositoryInterface

`RepositoryInterface` — это абстрактный базовый класс с поддержкой generic-типов, предназначенный для определения интерфейса репозиториев в проекте **Chalkboard OCR Classification Kit**. Он задаёт контракт для работы с данными в различных хранилищах (например, MongoDB, PostgreSQL и других).

!!! info
    Все методы выбрасывают `NotImplementedError`, чтобы предотвратить использование интерфейса напрямую. Реализация должна быть предоставлена в классах-наследниках.

## Методы

### `get_one(query: dict[str, Any]) -> T | None`
Ищет и возвращает один объект по заданному запросу.

- **Параметры**:
  - `query: dict[str, Any]`: Фильтр для поиска (например, `{"id": "123"}`).
- **Возвращает**: Экземпляр объекта типа `T` или `None`, если ничего не найдено.
- **Выбрасывает**: `NotImplementedError`.

### `get_all(query: dict[str, Any]) -> List[T]`
Возвращает список всех объектов, соответствующих запросу.

- **Параметры**:
  - `query: dict[str, Any]`: Фильтр для поиска (опционально).
- **Возвращает**: Список объектов типа `T`.
- **Выбрасывает**: `NotImplementedError`.

### `add(entity: T) -> T`
Создаёт новый объект в хранилище.

- **Параметры**:
  - `entity: T`: Данные для создания объекта.
- **Возвращает**: Созданный объект типа `T`.
- **Выбрасывает**: `NotImplementedError`.

### `get_or_create(entity: T) -> Tuple[T, bool]`
Ищет объект по критериям, а если он не найден — создаёт новый.

- **Параметры**:
  - `entity: T`: Данные для поиска или создания.
- **Возвращает**: Кортеж из объекта типа `T` и булева значения (`True`, если создан; `False`, если найден).
- **Выбрасывает**: `NotImplementedError`.

### `update(query: dict[str, Any], entity: T) -> T`
Обновляет существующий объект по заданному запросу.

- **Параметры**:
  - `query: dict[str, Any]`: Фильтр для поиска объекта.
  - `entity: T`: Данные для обновления.
- **Возвращает**: Обновлённый объект типа `T`.
- **Выбрасывает**: `NotImplementedError`.

### `delete(query: dict[str, Any]) -> bool`
Удаляет объект по заданному запросу.

- **Параметры**:
  - `query: dict[str, Any]`: Фильтр для поиска объекта.
- **Возвращает**: Булево значение (`True`, если объект удалён; `False`, если объект не найден).
- **Выбрасывает**: `NotImplementedError`.

## Пример использования
Класс `RepositoryInterface` задаёт контракт для всех репозиториев с использованием generic-типов. Пример наследования:

```python
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

class CustomRepo(RepositoryInterface[dict[str, Any]]):
    async def get_one(self, query: dict[str, Any]) -> dict[str, Any] | None:
        # Реализация поиска одного объекта
        pass

    async def get_all(self, query: dict[str, Any]) -> List[dict[str, Any]]:
        # Реализация поиска всех объектов
        pass

    async def add(self, entity: dict[str, Any]) -> dict[str, Any]:
        # Реализация создания объекта
        pass

    async def get_or_create(self, entity: dict[str, Any]) -> Tuple[dict[str, Any], bool]:
        # Реализация поиска или создания
        pass

    async def update(self, query: dict[str, Any], entity: dict[str, Any]) -> dict[str, Any]:
        # Реализация обновления объекта
        pass

    async def delete(self, query: dict[str, Any]) -> bool:
        # Реализация удаления объекта
        pass
```

!!! note
    Интерфейс может быть расширен новыми методами по мере развития проекта.