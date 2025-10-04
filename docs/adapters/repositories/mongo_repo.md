# MongoRepo

`MongoRepo` — это реализация интерфейса `RepositoryInterface` для работы с MongoDB в проекте **Chalkboard OCR Classification Kit**. Использует библиотеку `motor` для асинхронного взаимодействия с MongoDB и `pydantic` для валидации данных.

!!! info
    Класс предназначен для работы с коллекцией MongoDB. Все методы возвращают данные в формате словарей

## Инициализация

```python
from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic import BaseModel
from app.repositories.mongo_repo import MongoRepo

class MyModel(BaseModel):
    id: str
    name: str

collection = AsyncIOMotorCollection(...)  # Коллекция MongoDB
repo = MongoRepo(collection=collection, model=MyModel)
```

- **Параметры**:
  - `collection: AsyncIOMotorCollection`: Коллекция MongoDB для работы.
  - `model: Type[BaseModel]`: Pydantic-модель для валидации данных.

## Методы

### `get_one(query: dict[str, Any]) -> Optional[dict[str, Any]]`
Ищет и возвращает один документ по заданному запросу.

- **Параметры**:
  - `query: dict[str, Any]`: Фильтр для поиска (например, `{"id": "123"}`).
- **Возвращает**: Словарь, соответствующий Pydantic-модели, или `None`, если документ не найден.

**Пример**:
```python
document = await repo.get_one({"id": "123"})
if document:
    print(document["name"])  # Доступ к полям словаря
```

### `get_all(query: dict[str, Any]) -> List[dict[str, Any]]`
Возвращает список всех документов, соответствующих запросу.

- **Параметры**:
  - `query: dict[str, Any]`: Фильтр для поиска (опционально, например, `{}` для всех документов).
- **Возвращает**: Список словарей, соответствующих Pydantic-модели.

**Пример**:
```python
documents = await repo.get_all({})
for doc in documents:
    print(doc["name"])
```

### `add(document: dict[str, Any]) -> dict[str, Any]`
Создаёт новый документ в коллекции.

- **Параметры**:
  - `document: dict[str, Any]`: Данные для создания документа.
- **Возвращает**: Словарь, соответствующий созданной Pydantic-модели.

**Пример**:
```python
new_doc = await repo.add({"id": "123", "name": "Example"})
print(new_doc["id"])  # "123"
```

### `get_or_create(document: dict[str, Any]) -> Tuple[dict[str, Any], bool]`
Ищет документ по критериям, а если он не найден — создаёт новый.

- **Параметры**:
  - `document: dict[str, Any]`: Данные для поиска или создания.
- **Возвращает**: Кортеж из словаря (Pydantic-модель) и флага (`True`, если создан; `False`, если найден).

**Пример**:
```python
doc, created = await repo.get_or_create({"id": "123", "name": "Example"})
print(doc["name"], created)  # "Example", True (или False, если уже существует)
```

### `update(query: dict[str, Any], update_data: dict[str, Any]) -> dict[str, Any]`
Обновляет существующий документ по заданному запросу.

- **Параметры**:
  - `query: dict[str, Any]`: Фильтр для поиска документа.
  - `update_data: dict[str, Any]`: Данные для обновления.
- **Возвращает**: Словарь, соответствующий обновлённой Pydantic-модели.

**Пример**:
```python
updated_doc = await repo.update({"id": "123"}, {"name": "New Name"})
print(updated_doc["name"])  # "New Name"
```

## Примечания
- Все методы используют Pydantic для валидации данных, обеспечивая типобезопасность.
- Метод `model_dump(exclude_unset=True)` исключает неустановленные поля при создании или обновлении.
- Для работы требуется настроенная коллекция MongoDB через `motor.motor_asyncio`.
- Все возвращаемые данные преобразуются в словари через `model_dump()` для соответствия интерфейсу.