## Класс UserCreateDTO

**Данные для создания пользователя.**

**Args:**
- `username`: Имя пользователя
- `email`: Email пользователя
- `password`: Пароль пользователя
- `repeat_password`: Повтор пароля пользователя
## Класс UserDTO

**Данные о пользователе, возвращаемые пользователю.**

**Args:**
- `id`: Уникальный идентификатор пользователя
- `username`: Имя пользователя
- `email`: Email пользователя

---
### fromrow
**Создает экземпляр класса из словаря.**

```python
    @classmethod
    def fromrow(cls, row: dict[str, Any]) -> UserDTO:
        """Создает экземпляр класса из словаря."""
        return cls(
            id=str(row.get("_id") or row.get("id")),
            username=row["username"],
            email=row["email"],
        )
```
---
## Класс UserLoginDTO

**Данные для авторизации пользователя.**

**Args:**
- `identifier`: Email или username пользователя
- `password`: Пароль пользователя