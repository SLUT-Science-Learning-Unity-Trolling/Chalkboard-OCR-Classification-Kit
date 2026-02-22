## Класс TokenClaims

**Представляет набор базовых claims (утверждений) для PASETO токена.**

Этот класс описывает информацию, которую содержит токен для идентификации
пользователя и определения типа токена (access или refresh).

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `sub` | `str` | Уникальный идентификатор субъекта (пользователя). |
| `type` | `Literal["access", "refresh"]` | Тип токена. |
| `jti` | `str` | Уникальный идентификатор токена (JWT ID / Token ID). |
| `username` | `str \| None` | Имя пользователя, связанное с токеном. (optional) |
| `email` | `str \| None` | Email пользователя, связанный с токеном. (optional) |

```python
@dataclass(frozen=True, slots=True)
class TokenClaims:
    """
    Представляет набор базовых claims (утверждений) для PASETO токена.

    Этот класс описывает информацию, которую содержит токен для идентификации
    пользователя и определения типа токена (access или refresh).

    Attributes:
        sub (str): Уникальный идентификатор субъекта (пользователя).
        type (Literal["access", "refresh"]): Тип токена.
        jti (str): Уникальный идентификатор токена (JWT ID / Token ID).
        username (str | None, optional): Имя пользователя, связанное с токеном. 
        email (str | None, optional): Email пользователя, связанный с токеном.
    """
    sub: str
    type: Literal["access", "refresh"]
    jti: str
    username: str | None = None
    email: str | None = None
```