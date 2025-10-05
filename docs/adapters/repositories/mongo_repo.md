## Класс MongoRepo

**Асинхронный репозиторий для работы с MongoDB.**
Репозиторий инкапсулирует работу с коллекцией MongoDB, предоставляя
CRUD операции для работы с документами.

---
## def init:
#### Инициализация репозитория.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `gateway` | `DBGatewayInterface` | Объект для работы с базой данных. |
| `collection_name` | `str` | Название коллекции MongoDB. |

```python
    def __init__(
        self, gateway: DBGatewayInterface, collection_name: str
    ) -> None:
        """Инициализация репозитория.

        Args:
            gateway (DBGatewayInterface): Объект для работы с базой данных.
            collection_name (str): Название коллекции MongoDB.
        """
        self.__gw = gateway
        self.collection_name = collection_name
```
---
## async def _init_collection:
#### Получение асинхронного объекта коллекции.

#### Возвращает
| Тип | Описание |
|-----|----------|
| `AsyncCollection` | Асинхронная коллекция MongoDB. |

```python
    async def _init_collection(self) -> AsyncCollection:
        """Получение асинхронного объекта коллекции.

        Returns:
            AsyncCollection: Асинхронная коллекция MongoDB.
        """
        return await self.__gw.get_collection(self.collection_name)  # type: ignore
```
---
## async def add:
#### Добавляет новый документ в коллекцию.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `data` | `dict[str, Any]` | Словарь с данными документа. |

#### Возвращает
| Тип | Описание |
|-----|----------|
| `ObjectId` | Уникальный идентификатор добавленного документа. |

```python
    async def add(self, data: dict[str, Any]) -> ObjectId:
        """Добавляет новый документ в коллекцию.

        Args:
            data (dict[str, Any]): Словарь с данными документа.

        Returns:
            ObjectId: Уникальный идентификатор добавленного документа.
        """
        collection = await self._init_collection()
        result = await collection.insert_one(data)
        return result.inserted_id
```
---
## async def get_one:
#### Получает один документ из коллекции по условию.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `query` | `dict[str, Any]` | Словарь с фильтром поиска. |

#### Возвращает
| Тип | Описание |
|-----|----------|
| `dict[str, Any] | None` | Найденный документ или None, если не найден. |

```python
    async def get_one(self, query: dict[str, Any]) -> dict[str, Any]:
        """Получает один документ из коллекции по условию.

        Args:
            query (dict[str, Any]): Словарь с фильтром поиска.

        Returns:
            dict[str, Any] | None: Найденный документ или None, если не найден.
        """
        collection = await self._init_collection()
        result = await collection.find_one(query)
        return result
```
---
## async def get_many:
#### Получает несколько документов из коллекции.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `query` | `dict[str, Any]` | Словарь с фильтром поиска. |
| `limit` | `int, optional` | Максимальное количество документов. По умолчанию 10. |

#### Возвращает
| Тип | Описание |
|-----|----------|
| `list[dict[str, Any]]` | Список найденных документов. |

```python
    async def get_many(
        self, query: dict[str, Any], limit: int = 10
    ) -> list[dict[str, Any]]:
        """Получает несколько документов из коллекции.

        Args:
            query (dict[str, Any]): Словарь с фильтром поиска.
            limit (int, optional): Максимальное количество документов. По умолчанию 10.

        Returns:
            list[dict[str, Any]]: Список найденных документов.
        """
        collection = await self._init_collection()
        result = collection.find(query).limit(limit)
        return await result.to_list()
```
---
## async def update:
#### Обновляет один документ в коллекции.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `query` | `dict[str, Any]` | Словарь с фильтром поиска документа. |
| `update_data` | `dict[str, Any]` | Данные для обновления (например, {"$set": {...}}). |

#### Возвращает
| Тип | Описание |
|-----|----------|
| `dict[str, Any] | None` | Обновленный документ или None, если документ не найден. |

```python
    async def update(
        self, query: dict[str, Any], update_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Обновляет один документ в коллекции.

        Args:
            query (dict[str, Any]): Словарь с фильтром поиска документа.
            update_data (dict[str, Any]): Данные для обновления (например, {"$set": {...}}).

        Returns:
            dict[str, Any] | None: Обновленный документ или None, если документ не найден.
        """
        collection = await self._init_collection()
        result = await collection.find_one_and_update(
            filter=query, update=update_data
        )
        return result
```
---
## async def delete:
#### Удаляет один документ из коллекции.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `query` | `dict[str, Any]` | Словарь с фильтром для удаления. |

#### Возвращает
| Тип | Описание |
|-----|----------|
| `bool` | True, если документ был успешно удален, иначе False. |

#### Исключения
| Исключение | Описание |
|------------|----------|
| `ValueError` | Если возникла ошибка при удалении документа. |

```python
    async def delete(self, query: dict[str, Any]) -> bool:
        """Удаляет один документ из коллекции.

        Args:
            query (dict[str, Any]): Словарь с фильтром для удаления.

        Returns:
            bool: True, если документ был успешно удален, иначе False.

        Raises:
            ValueError: Если возникла ошибка при удалении документа.
        """
        try:
            collection = await self._init_collection()
            await collection.find_one_and_delete(query)
            return True
        except Exception as e:
            raise ValueError(e)
```
---