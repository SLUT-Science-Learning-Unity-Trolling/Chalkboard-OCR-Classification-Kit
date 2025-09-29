# UserService

Сервис для работы с пользователями. Отвечает за бизнес-логику, связанную с созданием и управлением сущностью `User`.

---

## Класс: `UserService`

```python
from app.core.models.user import User
from app.infrastructure.repositories.__abc_repo__ import RepositoryInterface
```

### Конструктор

```python
UserService(repository: RepositoryInterface) -> None
```

**Описание:**
Инициализирует сервис с переданным репозиторием пользователей.
Использует абстрактный интерфейс `RepositoryInterface`, что позволяет легко подменять реализацию (например, MongoDB, PostgreSQL или In-Memory).

**Параметры:**

* `repository (RepositoryInterface)` — реализация интерфейса репозитория.

---

### Метод: `create_user`

```python
async def create_user(self, username: str, email: str) -> User
```

**Описание:**
Создаёт нового пользователя и сохраняет его в репозиторий.

**Параметры:**

* `username (str)` — имя пользователя.
* `email (str)` — email пользователя.

**Возвращает:**

* `User` — созданный объект пользователя.

**Исключения:**

* `ValueError` — если пользователь не был создан (репозиторий вернул `None`).

---

## Использование

```python
from app.core.services.user_service import UserService
from app.infrastructure.repositories.user_repo import UserRepository

repo = UserRepository()
service = UserService(repo)

user = await service.create_user("ivan", "ivan@example.com")
print(user.username)  # ivan
```