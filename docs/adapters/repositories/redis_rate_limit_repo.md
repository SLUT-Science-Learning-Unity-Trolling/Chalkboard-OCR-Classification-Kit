# Модуль redis_rate_limit_repo

Модуль содержит репозиторий для работы с Redis (rate limiting).

## Класс RedisRateLimitRepo

**Репозиторий для работы с rate limit в Redis.**

```python
class RedisRateLimitRepo:
    """Репозиторий для работы с rate limit в Redis."""
```

---
## def init:
#### Инициализация репозитория.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `gateway` | `RedisGateway` | Гейтвей для подключения к Redis. |

```python
    def __init__(self, gateway: RedisGateway) -> None:
        """Инициализация репозитория.

        Args:
            gateway (RedisGateway): Гейтвей для подключения к Redis.
        """
        self._gateway = gateway
```
---
## def _key:
#### Генерация ключа для rate limit с указанием действия.

```python
    def _key(self, key: str, action: str) -> str:
        """Генерация ключа для rate limit с указанием действия."""
        return f"rl:{key}:{action}"
```
---
## async def increment:
#### Увеличивает счетчик запросов и устанавливает TTL при первом обращении.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `key` | `str` | Ключ (ip или user_id). |
| `action` | `str` | Тип действия (login, refresh и т.д.). |
| `window` | `int` | Время окна в секундах. |

#### Возвращает
| Тип | Описание |
|-----|----------|
| `int` | Текущее количество запросов. |

```python
    async def increment(self, key: str, action: str, window: int) -> int:
        """Увеличивает счетчик запросов и устанавливает TTL при первом обращении.

        Args:
            key (str): Ключ (ip или user_id).
            action (str): Тип действия (login, refresh и т.д.).
            window (int): Время окна в секундах.

        Returns:
            int: Текущее количество запросов.
        """
        client = await self._gateway.get_connection()
        redis_key = self._key(key, action)

        current = await client.incr(redis_key)

        if current == 1:
            await client.expire(redis_key, window)

        return current
```
---
## async def is_allowed:
#### Проверяет, разрешен ли запрос в рамках лимита и возвращает retry_after.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `key` | `str` | Ключ (ip или user_id). |
| `action` | `str` | Тип действия (login, refresh и т.д.). |
| `limit` | `int` | Максимальное количество запросов. |
| `window` | `int` | Время окна в секундах. |

#### Возвращает
| Тип | Описание |
|-----|----------|
| `tuple[bool, int | None]` | (Разрешён ли запрос, время до разблокировки в секундах) |

```python
    async def is_allowed(
        self, key: str, action: str, limit: int, window: int
    ) -> tuple[bool, int | None]:
        """Проверяет, разрешен ли запрос в рамках лимита и возвращает retry_after.

        Args:
            key (str): Ключ (ip или user_id).
            action (str): Тип действия (login, refresh и т.д.).
            limit (int): Максимальное количество запросов.
            window (int): Время окна в секундах.

        Returns:
            tuple[bool, int | None]: (Разрешён ли запрос, время до разблокировки в секундах)
        """
        client = await self._gateway.get_connection()
        redis_key = self._key(key, action)

        current = await self.increment(key, action, window)

        if current <= limit:
            return True, None

        ttl = await client.ttl(redis_key)
        retry_after = int(ttl) if ttl and ttl > 0 else None

        return False, retry_after
```
---