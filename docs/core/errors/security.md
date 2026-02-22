# Модуль security

Модуль, содержащий исключения для сервиса безопасности.

## Класс TooManyRequestsError

**Исключение, возникающее при превышении лимита запросов.**

```python
class TooManyRequestsError(Exception):
    """Исключение, возникающее при превышении лимита запросов."""
```

---
## def init:
#### Конструктор.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `message` | `str \| Exception` | Сообщение об ошибке". (optional) |

```python
    def __init__(self, message: str | Exception = "Превышен лимит запросов.", retry_after: int | None = None) -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
        """
        super().__init__(message)
        self.message = message
        self.retry_after = retry_after
```
---
## Класс InvalidTokenError

**Исключение, возникающее при невалидном токене.**

```python
class InvalidTokenError(Exception):
    """Исключение, возникающее при невалидном токене."""
```

---
## def init:
#### Конструктор.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `message` | `str \| Exception` | Сообщение об ошибке". (optional) |

```python
    def __init__(self, message: str | Exception = "Сессия не действительна.") -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
        """
        super().__init__(message)
        self.message: str | Exception = message
```
---