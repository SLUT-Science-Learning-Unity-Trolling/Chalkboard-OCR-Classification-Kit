# Модуль redis_blacklist_repo

Модуль содержит репозиторий для работы с Redis (например, для blacklist refresh токенов).

## Класс RedisBlacklistRepo

**Репозиторий для работы с Redis.**

```python
class RedisBlacklistRepo:
    """Репозиторий для работы с Redis."""
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

```python
    def _key(self, jti: str) -> str:
        return f"bl:{jti}"
```
---
## async def add_to_blacklist:
#### Добавляет JTI токена в blacklist с указанием времени жизни.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `jti` | `str` | Идентификатор refresh токена. |
| `expires_in` | `int` | Время жизни в секундах. |

```python
    async def add_to_blacklist(self, jti: str, expires_in: int) -> None:
        """Добавляет JTI токена в blacklist с указанием времени жизни.

        Args:
            jti (str): Идентификатор refresh токена.
            expires_in (int): Время жизни в секундах.
        """
        client = await self._gateway.get_connection()
        await client.set(self._key(jti), "1", ex=expires_in)
```
---
## async def is_blacklisted:
#### Проверяет, находится ли JTI токена в blacklist.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `jti` | `str` | Идентификатор refresh токена. |

#### Возвращает
| Тип | Описание |
|-----|----------|
| `bool` | True, если токен в blacklist, иначе False. |

```python
    async def is_blacklisted(self, jti: str) -> bool:
        """Проверяет, находится ли JTI токена в blacklist.

        Args:
            jti (str): Идентификатор refresh токена.

        Returns:
            bool: True, если токен в blacklist, иначе False.
        """
        client = await self._gateway.get_connection()
        exists = await client.exists(self._key(jti))
        return bool(exists)
```
---
## async def remove_from_blacklist:
#### Удаляет JTI токена из blacklist (опционально).

```python
    async def remove_from_blacklist(self, jti: str) -> None:
        """Удаляет JTI токена из blacklist (опционально)."""
        client = await self._gateway.get_connection()
        await client.delete(self._key(jti))
```
---