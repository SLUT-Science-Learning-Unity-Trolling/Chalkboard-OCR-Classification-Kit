# Модуль abc_repo

Модуль содержит абстрактный репозиторий для работы с БД.

## Класс RepositoryInterface

**Базовый репозиторий для работы с с БД.**

```python
class RepositoryInterface(ABC):
    """Базовый репозиторий для работы с с БД."""
```

---
## def init:
#### Конструктор.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `gateway` | `DBGateway` | Гейт к бд. |

```python
    def __init__(self, gateway: DBGatewayInterface) -> None:
        """Конструктор.

        Args:
            gateway (DBGateway): Гейт к бд.
        """
        self.__gw = gateway
```
---
## def add:
#### Добавление нового документа/таблицы.

#### Возвращает
| Тип | Описание |
|-----|----------|
| `Any` | ID нового объекта |

```python
    @abstractmethod
    async def add(self, data: dict[str, Any]) -> Any:
        """Добавление нового документа/таблицы.

        Returns:
            Any: ID нового объекта
        """
        raise NotImplementedError
```
---
## def get_one:
#### Получение одного объекта.

```python
    @abstractmethod
    async def get_one(self, query: dict[str, Any]) -> dict[str, Any]:
        """Получение одного объекта."""
        raise NotImplementedError
```
---
## def get_many:
#### Получение нескольких объектов.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `query` | `dict[str, Any]` | Поисковый запрос |
| `limit` | `int` | Кол-во объектов |

#### Возвращает
| Тип | Описание |
|-----|----------|
| `list[dict[str, Any]]` | Результат поиска |

```python
    @abstractmethod
    async def get_many(self, query: dict[str, Any], limit: int) -> list[dict[str, Any]]:
        """Получение нескольких объектов.

        Args:
            query (dict[str, Any]): Поисковый запрос
            limit (int): Кол-во объектов

        Returns:
            list[dict[str, Any]]: Результат поиска
        """
        raise NotImplementedError
```
---
## def update:
#### Обновление объекта.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `query` | `dict[str, Any]` | Поисковый запрос |
| `update_data` | `dict[str, Any]` | Данные для обновления |

#### Возвращает
| Тип | Описание |
|-----|----------|
| `dict[str, Any]` | Обновленный объект |

```python
    @abstractmethod
    async def update(
        self, query: dict[str, Any], update_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Обновление объекта.

        Args:
            query (dict[str, Any]): Поисковый запрос
            update_data (dict[str, Any]): Данные для обновления

        Returns:
            dict[str, Any]: Обновленный объект
        """
        raise NotImplementedError
```
---
## def delete:
#### Удаление объекта.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `query` | `dict[str, Any]` | Поисковый запрос |

#### Возвращает
| Тип | Описание |
|-----|----------|
| `bool` | Результат операции |

```python
    @abstractmethod
    async def delete(self, query: dict[str, Any]) -> bool:
        """Удаление объекта.

        Args:
            query (dict[str, Any]): Поисковый запрос

        Returns:
            bool: Результат операции
        """
        raise NotImplementedError
```
---