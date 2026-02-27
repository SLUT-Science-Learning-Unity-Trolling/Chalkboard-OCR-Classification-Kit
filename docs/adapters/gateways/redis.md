# Модуль redis

Модуль содержит класс RedisGateway для подключения к Redis.

## Класс RedisGateway

**Класс для работы с Redis.**

```python
class RedisGateway:
    """Класс для работы с Redis."""
```

---
## def init:
#### Конструктор.

Инициализирует параметры подключения, но соединение не создается сразу.

```python
    def __init__(self, db: int) -> None:
        """Конструктор.

        Инициализирует параметры подключения, но соединение не создается сразу.
        """
        self._host = config.REDIS_HOST
        self._port = config.REDIS_PORT
        self._db = db
        self._password = config.REDIS_PASSWORD
        self._client: redis.Redis | None = None
```
---
## async def connect:
#### Устанавливает соединение с Redis.

```python
    async def connect(self) -> None:
        """Устанавливает соединение с Redis."""
        if not self._client:
            self._client = redis.Redis(
                host=self._host,
                port=self._port,
                db=self._db,
                password=self._password,
                decode_responses=True,
            )
        try:
            pong: bool = self._client.ping()
            if not pong:
                raise ConnectionError("Redis did not respond to PING")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Redis: {str(e)}") from e
```
---
## async def get_connection:
#### Возвращает клиент Redis, подключаясь при необходимости.

```python
    async def get_connection(self) -> redis.Redis | None:
        """Возвращает клиент Redis, подключаясь при необходимости."""
        if not self._client:
            await self.connect()
        return self._client
```
---
## async def close:
#### Закрывает соединение с Redis.

```python
    async def close(self) -> None:
        """Закрывает соединение с Redis."""
        if self._client:
            await self._client.close()
            self._client = None
```
---