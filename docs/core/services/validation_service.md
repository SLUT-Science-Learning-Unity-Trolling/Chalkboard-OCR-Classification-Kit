# Модуль validation_service

Модуль содержит класс ValidationService для валидации данных.

## Класс ValidationService

**Сервис для валидации пользовательских данных.**

Методы класса обеспечивают:
    - Проверку пароля по требованиям безопасности.
    - Проверку имени пользователя (username).
    - Проверку email.
    - Комплексную проверку учетных данных.
    - Проверку допустимости загружаемых файлов (изображений).

```python
class ValidationService:
    """Сервис для валидации пользовательских данных.

    Методы класса обеспечивают:
        - Проверку пароля по требованиям безопасности.
        - Проверку имени пользователя (username).
        - Проверку email.
        - Комплексную проверку учетных данных.
        - Проверку допустимости загружаемых файлов (изображений).
    """

    __slots__ = ("_config")

    EMAIL_REGEX: Final[re.Pattern[str]] = re.compile(
        r"^(?=.{1,64}@)[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    )
    USERNAME_REGEX: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9_-]+$")
    WHITESPACE_REGEX: Final[re.Pattern[str]] = re.compile(r"\s")
```

---
## def init:
#### Инициализация сервиса валидации.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `config_class` | `` | Класс конфигурации (по умолчанию Config) |

```python
    def __init__(self, config_class: type[config.Config] = config.Config) -> None:
        """Инициализация сервиса валидации.

        Args:
            config_class: Класс конфигурации (по умолчанию Config)
        """
        self._config = config_class
```
---
## def config:
#### Возвращает класс конфигурации.

```python
    @property
    def config(self) -> type[config.Config]:
        """Возвращает класс конфигурации."""
        return self._config
```
---
## def validate_password:
#### Проверка пароля на соответствие требованиям безопасности.

Требования:
- Не пустой
- Без пробелов
- Минимальная длина
- Хотя бы одна цифра
- Хотя бы одна заглавная буква
- Хотя бы одна строчная буква
- Хотя бы один спецсимвол

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `password` | `` | Пароль для проверки |

#### Исключения
| Исключение | Описание |
|------------|----------|
| `PasswordValidationError` | При несоответствии требованиям |

```python
    def validate_password(self, password: str) -> None:
        """Проверка пароля на соответствие требованиям безопасности.

        Требования:
        - Не пустой
        - Без пробелов
        - Минимальная длина
        - Хотя бы одна цифра
        - Хотя бы одна заглавная буква
        - Хотя бы одна строчная буква
        - Хотя бы один спецсимвол

        Args:
            password: Пароль для проверки

        Raises:
            PasswordValidationError: При несоответствии требованиям
        """
        if not password:
            raise PasswordValidationError("Пароль не должен быть пустым")

        if len(password) < self._config.PASSWORD_MIN_LENGTH:
            raise PasswordValidationError(
                f"Пароль должен содержать минимум "
                f"{self._config.PASSWORD_MIN_LENGTH} символов"
            )

        if self.WHITESPACE_REGEX.search(password):
            raise PasswordValidationError("Пароль не должен содержать пробелы")

        self._check_password_complexity(password)
```
---
## def _check_password_complexity:
#### Проверка сложности пароля (наличие разных типов символов).

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `password` | `` | Пароль для проверки |

#### Исключения
| Исключение | Описание |
|------------|----------|
| `PasswordValidationError` | При отсутствии требуемых символов |

```python
    def _check_password_complexity(self, password: str) -> None:
        """Проверка сложности пароля (наличие разных типов символов).

        Args:
            password: Пароль для проверки

        Raises:
            PasswordValidationError: При отсутствии требуемых символов
        """
        has_digit = False
        has_upper = False
        has_lower = False
        has_special = False
        checks_remaining = 4

        for char in password:
            if not has_digit and char.isdigit():
                has_digit = True
                checks_remaining -= 1
            elif not has_upper and char.isupper():
                has_upper = True
                checks_remaining -= 1
            elif not has_lower and char.islower():
                has_lower = True
                checks_remaining -= 1
            elif not has_special and char in self._config.PASSWORD_SPEC_SYMBOLS:
                has_special = True
                checks_remaining -= 1

            if checks_remaining == 0:
                return

        self._raise_password_complexity_error(
            has_digit, has_upper, has_lower, has_special
        )
```
---
## def _raise_password_complexity_error:
#### Выбрасывает исключение с описанием недостающего требования.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `has_digit` | `` | Флаг наличия цифры |
| `has_upper` | `` | Флаг наличия заглавной буквы |
| `has_lower` | `` | Флаг наличия строчной буквы |
| `has_special` | `` | Флаг наличия спецсимвола |

#### Исключения
| Исключение | Описание |
|------------|----------|
| `PasswordValidationError` | Всегда выбрасывается с соответствующим сообщением |

```python
    def _raise_password_complexity_error(
        self,
        has_digit: bool,
        has_upper: bool,
        has_lower: bool,
        has_special: bool,
    ) -> None:
        """Выбрасывает исключение с описанием недостающего требования.

        Args:
            has_digit: Флаг наличия цифры
            has_upper: Флаг наличия заглавной буквы
            has_lower: Флаг наличия строчной буквы
            has_special: Флаг наличия спецсимвола

        Raises:
            PasswordValidationError: Всегда выбрасывается с соответствующим сообщением
        """
        if not has_digit:
            raise PasswordValidationError(
                "Пароль должен содержать хотя бы одну цифру"
            )
        if not has_upper:
            raise PasswordValidationError(
                "Пароль должен содержать хотя бы одну заглавную букву"
            )
        if not has_lower:
            raise PasswordValidationError(
                "Пароль должен содержать хотя бы одну строчную букву"
            )
        if not has_special:
            raise PasswordValidationError(
                f"Пароль должен содержать хотя бы один спецсимвол из "
                f"{self._config.PASSWORD_SPEC_SYMBOLS}"
            )
```
---
## def validate_username:
#### Проверка имени пользователя.

Требования:
- Не пустое
- Минимальная и максимальная длина
- Только латинские буквы, цифры, _ и -

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `username` | `` | Имя пользователя |

#### Исключения
| Исключение | Описание |
|------------|----------|
| `UsernameValidationError` | При несоответствии требованиям |

```python
    def validate_username(self, username: str) -> None:
        """Проверка имени пользователя.

        Требования:
        - Не пустое
        - Минимальная и максимальная длина
        - Только латинские буквы, цифры, _ и -

        Args:
            username: Имя пользователя

        Raises:
            UsernameValidationError: При несоответствии требованиям
        """
        if not username:
            raise UsernameValidationError("Имя пользователя не должно быть пустым")

        username_len = len(username)

        if username_len < self._config.USERNAME_MIN_LENGTH:
            raise UsernameValidationError(
                f"Имя пользователя должно содержать минимум "
                f"{self._config.USERNAME_MIN_LENGTH} символов"
            )

        if username_len > self._config.USERNAME_MAX_LENGTH:
            raise UsernameValidationError(
                f"Имя пользователя не должно превышать "
                f"{self._config.USERNAME_MAX_LENGTH} символов"
            )

        if not self.USERNAME_REGEX.fullmatch(username):
            raise UsernameValidationError(
                "Имя пользователя может содержать только "
                "латинские буквы, цифры, '_' и '-'"
            )
```
---
## def validate_email:
#### Проверка email.

Требования:
- Не пустой
- Корректный формат (RFC 5321)
- Максимальная длина 254 символа

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `email` | `` | Email для валидации |

#### Исключения
| Исключение | Описание |
|------------|----------|
| `EmailValidationError` | При несоответствии требованиям |

```python
    def validate_email(self, email: str) -> None:
        """Проверка email.

        Требования:
        - Не пустой
        - Корректный формат (RFC 5321)
        - Максимальная длина 254 символа

        Args:
            email: Email для валидации

        Raises:
            EmailValidationError: При несоответствии требованиям
        """
        if not email:
            raise EmailValidationError("Email не может быть пустым")

        if len(email) > self._config.EMAIL_MAX_LENGTH:
            raise EmailValidationError(
                f"Email не должен превышать {self._config.EMAIL_MAX_LENGTH} символов"
            )

        if not self.EMAIL_REGEX.fullmatch(email):
            raise EmailValidationError("Некорректный формат email")
```
---
## def validate_credentials:
#### Общая валидация учетных данных для регистрации и логина.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `identifier` | `` | Email или username пользователя |
| `password` | `` | Пароль пользователя |
| `is_email` | `` | True если identifier - это email, False если username |

#### Исключения
| Исключение | Описание |
|------------|----------|
| `IdentificatorIsNullError` | Если identifier пустой |
| `EmailValidationError` | Если email невалиден |
| `UsernameValidationError` | Если username невалиден |
| `PasswordValidationError` | Если пароль невалиден |

```python
    def validate_credentials(
        self,
        identifier: str | None,
        password: str,
        is_email: bool,
    ) -> None:
        """Общая валидация учетных данных для регистрации и логина.

        Args:
            identifier: Email или username пользователя
            password: Пароль пользователя
            is_email: True если identifier - это email, False если username

        Raises:
            IdentificatorIsNullError: Если identifier пустой
            EmailValidationError: Если email невалиден
            UsernameValidationError: Если username невалиден
            PasswordValidationError: Если пароль невалиден
        """
        if not identifier or not (identifier := identifier.strip()):
            raise IdentificatorIsNullError(
                "Имя пользователя или email не должны быть пустыми"
            )

        if is_email:
            self.validate_email(identifier.lower())
        else:
            self.validate_username(identifier)

        self.validate_password(password)
```
---
## def validate_image_file:
#### Проверка загружаемого изображения.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `file` | `` | Объект загружаемого файла |

#### Исключения
| Исключение | Описание |
|------------|----------|
| `ValueError` | Если файл не является допустимым изображением |

```python
    def validate_image_file(self, file: UploadFile) -> None:
        """Проверка загружаемого изображения.

        Args:
            file: Объект загружаемого файла

        Raises:
            ValueError: Если файл не является допустимым изображением
        """
        filename = file.filename
        if not filename:
            raise ValueError("Имя файла не может быть пустым")

        ext = os.path.splitext(filename)[1].lower().lstrip(".")

        if ext not in self._config.ALLOWED_IMAGE_EXTENSIONS:
            allowed = ", ".join(sorted(self._config.ALLOWED_IMAGE_EXTENSIONS))
            raise ValueError(
                f"Недопустимое расширение файла. Разрешены: {allowed}"
            )
```
---