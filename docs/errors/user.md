# User Errors

В этом модуле собраны ошибки, связанные с работой с пользователями.  
Исключения позволяют централизованно обрабатывать ошибки и упрощают отладку.

---

## Класс: `UserCreationError`

```python
class UserCreationError(Exception):
    """Исключение, возникающее при ошибке создания пользователя."""
    
    def __init__(self, message: str = "Failed to create user"):
        self.message = message
        super().__init__(self.message)
```

**Описание:**
Исключение выбрасывается, если при создании пользователя возникла ошибка.
Например, если репозиторий не смог сохранить пользователя в базе данных.

**Параметры конструктора:**

* `message (str, optional)` — сообщение об ошибке (по умолчанию `"Failed to create user"`).

---

## Использование

```python
from app.errors.user import UserCreationError

def create_user_safe(username: str, email: str):
    try:
        # Допустим, тут вызов сервиса
        user = await service.create_user(username, email)
        return user
    except Exception:
        raise UserCreationError(f"Не удалось создать пользователя {username}")
```

---

## Примечания

* Исключение унаследовано от стандартного `Exception`.
* Может использоваться в сервисном или репозиторном слое для более точного контроля ошибок.