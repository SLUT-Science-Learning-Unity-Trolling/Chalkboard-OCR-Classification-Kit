# RepositoryInterface

`RepositoryInterface` — это абстрактный базовый класс, предназначенный для определения интерфейса репозиториев в проекте **Chalkboard OCR Classification Kit**. Он задаёт контракт для работы с данными в различных хранилищах (например, MongoDB, PostgreSQL и других).

!!! info
    Все методы выбрасывают `NotImplementedError`, чтобы предотвратить использование интерфейса напрямую. Реализация должна быть предоставлена в классах-наследниках.

## Методы

### `get_one(query: dict[str, Any]) -> Optional[dict[str, Any]]`
Ищет и возвращает один документ по заданному запросу.

- **Параметры**:
  - `query: dict[str, Any]`: Фильтр для поиска (например, `{"id": "123"}`).
- **Возвращает**: Экземпляр документа или `None`, если ничего не найдено.
- **Выбрасывает**: `NotImplementedError`.

### `get_all(query: dict[str, Any]) -> List[dict[str, Any]]`
Возвращает список всех документов, соответствующих запросу.

- **Параметры**:
  - `query: dict[str, Any]`: Фильтр для поиска (опционально).
- **Возвращает**: Список документов.
- **Выбрасывает**: `NotImplementedError`.

### `add(document: dict[str, Any]) -> dict[str, Any]`
Создаёт новый документ в хранилище.

- **Параметры**:
  - `document: dict[str, Any]`: Данные для создания документа.
- **Возвращает**: Созданный документ.
- **Выбрасывает**: `NotImplementedError`.

### `get_or_create(document: dict[str, Any]) -> Tuple[dict[str, Any], bool]`
Ищет документ по критериям, а если он не найден — создаёт новый.

- **Параметры**:
  - `document: dict[str, Any]`: Данные для поиска или создания.
- **Возвращает**: Кортеж из документа и булева значения (`True`, если создан; `False`, если найден).
- **Выбрасывает**: `NotImplementedError`.

### `update(query: dict[str, Any], update_data: dict[str, Any]) -> dict[str, Any]`
Обновляет существующий документ по заданному запросу.

- **Параметры**:
  - `query: dict[str, Any]`: Фильтр для поиска документа.
  - `update_data: dict[str, Any]`: Данные для обновления.
- **Возвращает**: Обновлённый документ.
- **Выбрасывает**: `NotImplementedError`.

## Пример использования
Класс `RepositoryInterface` задаёт контракт для всех репозиториев. Пример наследования:

```python
from app.repositories.repository_interface import RepositoryInterface
from typing import Any, List, Optional, Tuple

class CustomRepo(RepositoryInterface):
    async def get_one(self, query: dict[str, Any]) -> Optional[dict[str, Any]]:
        # Реализация поиска одного документа
        pass

    async def get_all(self, query: dict[str, Any]) -> List[dict[str, Any]]:
        # Реализация поиска всех документов
        pass

    async def add(self, document: dict[str, Any]) -> dict[str, Any]:
        # Реализация создания документа
        pass

    async def get_or_create(self, document: dict[str, Any]) -> Tuple[dict[str, Any], bool]:
        # Реализация поиска или создания
        pass

    async def update(self, query: dict[str, Any], update_data: dict[str, Any]) -> dict[str, Any]:
        # Реализация обновления документа
        pass
```

!!! note
    Интерфейс может быть расширен новыми методами по мере развития проекта.