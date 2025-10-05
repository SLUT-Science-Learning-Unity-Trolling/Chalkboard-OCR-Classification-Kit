## Класс RepositoryInterface

**Базовый репозиторий для работы с с БД.**

---
### init
**Конструктор.**

**Args:**
- `gateway (DBGateway)`: Гейт к бд.

```python
    def __init__(self, gateway: DBGatewayInterface) -> None:
        """Конструктор.

        Args:
            gateway (DBGateway): Гейт к бд.
        """
        self.__gw = gateway
```
---
### add
**Добавление нового документа/таблицы.**

**Returns:**
- `Any: ID нового объекта`

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
### get_one
**Получение одного объекта.**

```python
    @abstractmethod
    async def get_one(self, query: dict[str, Any]) -> dict[str, Any]:
        """Получение одного объекта."""
        raise NotImplementedError
```
---
### get_many
**Получение нескольких объектов.**

```python
    @abstractmethod
    async def get_many(
        self, query: dict[str, Any], limit: int
    ) -> list[dict[str, Any]]:
        """Получение нескольких объектов."""
        raise NotImplementedError
```
---
### update
**Обновление объекта.**

```python
    @abstractmethod
    async def update(
        self, query: dict[str, Any], update_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Обновление объекта."""
        raise NotImplementedError
```
---
### delete
**Удаление объекта.**

```python
    @abstractmethod
    async def delete(self, query: dict[str, Any]) -> bool:
        """Удаление объекта."""
        raise NotImplementedError
```
---