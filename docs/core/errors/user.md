## Класс UserCreationError

**Исключение, возникающее при ошибке создания пользователя.**

---
### init
**Конструктор.**

**Args:**
- `message (str | Exception)`: Сообщение об ошибке.

```python
    def __init__(self, message: str | Exception) -> None:
        """Конструктор.

        Args:
            message (str | Exception): Сообщение об ошибке.
        """
        self.message: str | Exception = message
```
---