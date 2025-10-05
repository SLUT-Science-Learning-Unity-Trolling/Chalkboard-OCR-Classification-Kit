## Класс UserService

**Сервис для работы с пользователями.**

---
## def init:
#### Конструктор.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `repository` | `RepositoryInterface` | Репозиторий |
| `security` | `SecurityService` | Секьюрити сервис |
| `validator` | `ValidationService` | Сервис валидации |

```python
    def __init__(
        self,
        repository: RepositoryInterface,
        security: SecurityService,
        validator: ValidationService,
    ) -> None:
        """Конструктор.

        Args:
            repository (RepositoryInterface): Репозиторий
            security (SecurityService): Секьюрити сервис
            validator (ValidationService): Сервис валидации
        Returns:
            None
        """
        self._repo = repository
        self._security = security
        self._validator = validator
```
---
## async def create_user:
#### Создает нового пользователя.
Проверяет корректность пароля, уникальность имени пользователя и email,
валидирует email и создает хэш пароля.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `username` | `str` | Имя пользователя. |
| `email` | `str` | Email пользователя. |
| `password` | `str` | Пароль пользователя. |
| `repeat_password` | `str` | Подтверждение пароля. |

#### Возвращает
| Тип | Описание |
|-----|----------|
| `User` | Экземпляр созданного пользователя. |

#### Исключения
| Исключение | Описание |
|------------|----------|
| `PasswordDontMatch` | Если пароли не совпадают. |
| `PasswordValidationError` | Если пароль не проходит проверку валидатором. |
| `UsernameValidationError` | Если имя пользователя некорректное. |
| `UsernameAlreadyTaken` | Если имя пользователя уже занято. |
| `EmailAlreadyTaken` | Если email уже используется. |
| `EmailValidationError` | Если email некорректный. |
| `UserCreationError` | Если произошла ошибка при создании пользователя. |

```python
    async def create_user(
        self, username: str, email: str, password: str, repeat_password: str
    ) -> User:
        """Создает нового пользователя.

        Проверяет корректность пароля, уникальность имени пользователя и email,
        валидирует email и создает хэш пароля.

        Args:
            username (str): Имя пользователя.
            email (str): Email пользователя.
            password (str): Пароль пользователя.
            repeat_password (str): Подтверждение пароля.

        Returns:
            User: Экземпляр созданного пользователя.

        Raises:
            PasswordDontMatch: Если пароли не совпадают.
            PasswordValidationError: Если пароль не проходит проверку валидатором.
            UsernameValidationError: Если имя пользователя некорректное.
            UsernameAlreadyTaken: Если имя пользователя уже занято.
            EmailAlreadyTaken: Если email уже используется.
            EmailValidationError: Если email некорректный.
            UserCreationError: Если произошла ошибка при создании пользователя.
        """
        if password != repeat_password:
            raise PasswordDontMatch

        if not await self._validator.validate_password(password):
            raise PasswordValidationError

        if not await self._validator.validate_username(username):
            raise UsernameValidationError

        existing_user = await self.does_user_exists(username, email)
        if existing_user:
            if existing_user.get("username") == username:
                raise UsernameAlreadyTaken
            if existing_user.get("email") == email.lower():
                raise EmailAlreadyTaken

        try:
            validate_email(email, test_environment=config.Config.DEBUG)
        except EmailNotValidError:
            raise EmailValidationError("Введите корректный email")

        salt, _hash = self._security.hash_password(password)
        password_hash = self._security.serialize_hash(salt, _hash)

        user_data = {
            "username": username,
            "email": email.lower(),
            "password_hash": password_hash,
        }
        try:
            id = await self._repo.add(user_data)

        except Exception:
            raise UserCreationError("Произошла ошибка")

        user = await self._repo.get_one({"_id": id})

        return User(**user)
```
---
## async def get_user_by_id:
#### Возвращает пользователя по ID.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `user_id` | `str` | ID пользователя |

#### Возвращает
| Тип | Описание |
|-----|----------|
| `dict[str, Any]` | Пользователь |

```python
    async def get_user_by_id(self, user_id: str) -> dict[str, Any]:
        """Возвращает пользователя по ID.

        Args:
            user_id (str): ID пользователя

        Returns:
            dict[str, Any]: Пользователь
        """
        user = await self._repo.get_one({"_id": ObjectId(user_id)})
        return user
```
---
## async def does_user_exists:
#### Проверяет, существует ли пользователь по username или email.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `username` | `str` | Имя пользователя |
| `email` | `str` | Email пользователя |

#### Возвращает
| Тип | Описание |
|-----|----------|
| `dict[str, Any] | None` | Пользователь или None |

```python
    async def does_user_exists(
        self, username: str, email: str
    ) -> dict[str, Any] | None:
        """Проверяет, существует ли пользователь по username или email.

        Args:
            username (str): Имя пользователя
            email (str): Email пользователя

        Returns:
            dict[str, Any] | None: Пользователь или None
        """
        user = await self._repo.get_one({"username": username})
        if user:
            return user

        user = await self._repo.get_one({"email": email.lower()})
        return user
```
---