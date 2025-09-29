# User

`User` — это доменная модель пользователя в проекте **Chalkboard OCR Classification Kit**, реализованная с использованием `dataclass` для представления бизнес-логики.

## Описание

Класс `User` представляет пользователя с уникальным идентификатором, именем и email. Используется для работы с данными пользователя на уровне бизнес-логики.

## Атрибуты

- `_id: Union[str, UUID]`: Уникальный идентификатор пользователя (может быть строкой или UUID).
- `username: str`: Имя пользователя (должно содержать не менее 3 символов).
- `email: str`: Email пользователя (должен содержать символ `@`).

## Проверка данных

Класс выполняет валидацию данных в методе `__post_init__`:

- Проверяет, что длина `username` не менее 3 символов, иначе выбрасывает `ValueError`.
- Проверяет, что `email` содержит символ `@`, иначе выбрасывает `ValueError`.

## Свойства

### `id: str`
Возвращает строковое представление идентификатора пользователя (`_id`).

## Пример использования

```python
from uuid import UUID
from app.models.user import User

# Создание экземпляра пользователя
user = User(_id="123e4567-e89b-12d3-a456-426614174000", username="john_doe", email="john@example.com")
print(user.id)  # "123e4567-e89b-12d3-a456-426614174000"
print(user.username)  # "john_doe"
print(user.email)  # "john@example.com"

# Ошибка при неверном формате email
try:
    user = User(_id="123e4567-e89b-12d3-a456-426614174000", username="john_doe", email="invalid_email")
except ValueError as e:
    print(e)  # "Invalid email format"

# Ошибка при коротком имени пользователя
try:
    user = User(_id="123e4567-e89b-12d3-a456-426614174000", username="jd", email="john@example.com")
except ValueError as e:
    print(e)  # "Username must be at least 3 characters long"
```