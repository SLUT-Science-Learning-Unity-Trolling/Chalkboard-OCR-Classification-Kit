# Модуль user

Модуль, содержащий исключения для сервиса пользователей.

## Класс UserCreationError

**Исключение, возникающее при ошибке создания пользователя.**

---
## def init:
#### Конструктор.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `message` | `str | Exception` | Сообщение об ошибке. |

```python
    def __init__(self, message: str | Exception) -> None:
        """Конструктор.

        Args:
            message (str | Exception): Сообщение об ошибке.
        """
        self.message: str | Exception = message
```
---