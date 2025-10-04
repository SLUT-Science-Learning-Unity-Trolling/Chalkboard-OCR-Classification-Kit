# UserDTO

`UserDTO` — это Pydantic-модель для представления данных пользователя в проекте **Chalkboard OCR Classification Kit**. Используется для валидации и сериализации данных при взаимодействии с репозиториями и API.

## Описание

Класс `UserDTO` определяет структуру данных пользователя для передачи между слоями приложения (например, между API и репозиторием). Использует библиотеку `pydantic` для валидации данных.

## Атрибуты

- `id: str`: Уникальный идентификатор пользователя (по умолчанию генерируется как строка UUID с помощью `uuid4()`).
- `username: str`: Имя пользователя.
- `email: str`: Email пользователя.

## Пример использования

```python
from app.models.user_dto import UserDTO

# Создание экземпляра DTO
user_dto = UserDTO(id="123e4567-e89b-12d3-a456-426614174000", username="john_doe", email="john@example.com")
print(user_dto.id)  # "123e4567-e89b-12d3-a456-426614174000"
print(user_dto.username)  # "john_doe"
print(user_dto.email)  # "john@example.com"

# Создание DTO с автоматически сгенерированным ID
new_user_dto = UserDTO(username="jane_doe", email="jane@example.com")
print(new_user_dto.id)  # Случайный UUID, например, "550e8400-e29b-41d4-a716-446655440000"

# Сериализация в словарь
data = new_user_dto.model_dump()
print(data)  # {'id': '550e8400-e29b-41d4-a716-446655440000', 'username': 'jane_doe', 'email': 'jane@example.com'}
```

## Примечания

- Поле `id` автоматически генерируется с использованием `uuid4()`, если не указано явно.
- Модель автоматически валидирует данные, обеспечивая их корректность перед использованием в репозитории или API.
- Используется в сочетании с `MongoRepo` для преобразования данных в объекты бизнес-логики (`User`) и обратно.