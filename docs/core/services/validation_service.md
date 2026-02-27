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

    __slots__ = ("_config",)

    EMAIL_REGEX: re.Pattern[str] = re.compile(
        r"^(?=.{1,64}@)[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    )
    USERNAME_REGEX: re.Pattern[str] = re.compile(r"^[A-Za-z0-9_-]+$")
    WHITESPACE_REGEX: re.Pattern[str] = re.compile(r"\s")
```

---
## def init:
#### Инициализация валидатора изображений.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `config_instance` | `` | Конфигурация приложения. |

```python
    def __init__(self, config_instance: Config = app_config) -> None:
        """Инициализация валидатора изображений.

        Args:
            config_instance: Конфигурация приложения.
        """
        self._config = config_instance
```
---
## def config:
#### Конфигурация приложения.

```python
    @property
    def config(self) -> Config:
        """Конфигурация приложения."""
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
            raise PasswordValidationError("Пароль должен содержать хотя бы одну цифру")
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
## Класс ImageValidator

**Валидатор изображений с чёткой структурой и обработкой ошибок.**

```python
class ImageValidator:
    """Валидатор изображений с чёткой структурой и обработкой ошибок."""

    EXTENSION_TO_FORMAT: dict[str, str] = {
        "jpg": "JPEG",
        "jpeg": "JPEG",
        "png": "PNG",
        "gif": "GIF",
        "webp": "WEBP",
        "bmp": "BMP",
        "tiff": "TIFF",
        "tif": "TIFF",
    }
```

---
## def init:
#### Инициализация валидатора изображений.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `config` | `` | Конфигурация приложения. |

```python
    def __init__(self, config: Config) -> None:
        """Инициализация валидатора изображений.

        Args:
            config: Конфигурация приложения.
        """
        self._config = config
        self._allowed_extensions: frozenset[str] = frozenset(
            ext.lower().lstrip(".") for ext in self._config.ALLOWED_IMAGE_EXTENSIONS
        )
        self._allowed_formats: frozenset[str] = frozenset(
            self.EXTENSION_TO_FORMAT.get(ext, ext.upper())
            for ext in self._allowed_extensions
        )
```
---
## def validate_image_file:
#### Комплексная проверка загружаемого изображения.

Проверяет:
- Наличие имени файла
- Допустимость расширения
- Реальный формат изображения (через PIL)

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `file` | `` | Загружаемый файл FastAPI |

#### Исключения
| Исключение | Описание |
|------------|----------|
| `ImageValidationError` | Базовая ошибка валидации |
| `ImageExtensionValidationError` | Недопустимое расширение/формат |

```python
    def validate_image_file(self, file: UploadFile) -> None:
        """Комплексная проверка загружаемого изображения.

        Проверяет:
            - Наличие имени файла
            - Допустимость расширения
            - Реальный формат изображения (через PIL)

        Args:
            file: Загружаемый файл FastAPI
        Raises:
            ImageValidationError: Базовая ошибка валидации
            ImageExtensionValidationError: Недопустимое расширение/формат
        """
        filename = self._validate_filename(file)
        self._validate_extension(filename)
        self._validate_image_content(file)
```
---
## def _validate_filename:
#### Проверяет и возвращает имя файла.

```python
    def _validate_filename(self, file: UploadFile) -> str:
        """Проверяет и возвращает имя файла."""
        filename = getattr(file, "filename", None)

        if not filename or not filename.strip():
            raise ImageValidationError("Имя файла не может быть пустым")

        return filename
```
---
## def _validate_extension:
#### Проверяет расширение файла и возвращает его.

```python
    def _validate_extension(self, filename: str) -> str:
        """Проверяет расширение файла и возвращает его."""
        ext = self._extract_extension(filename)

        if ext not in self._allowed_extensions:
            allowed_str = ", ".join(f".{e}" for e in sorted(self._allowed_extensions))
            raise ImageExtensionValidationError(
                f"Недопустимое расширение файла: .{ext}. Разрешены: {allowed_str}"
            )

        return ext
```
---
## def _validate_image_content:
#### Проверяет, что содержимое файла — валидное изображение.

```python
    def _validate_image_content(self, file: UploadFile) -> None:
        """Проверяет, что содержимое файла — валидное изображение."""
        try:
            image_data = self._read_file_content(file)
            self._verify_image_format(image_data)
        except (ImageValidationError, ImageExtensionValidationError):
            raise
        except UnidentifiedImageError:
            raise ImageExtensionValidationError(
                "Файл не является допустимым изображением"
            ) from None
        except Exception:
            raise ImageValidationError("Ошибка валидации изображения") from None
```
---
## def _read_file_content:
#### Читает содержимое файла и сбрасывает позицию.

Обрабатывает разные типы file-like объектов.

```python
    def _read_file_content(self, file: UploadFile) -> bytes:
        """Читает содержимое файла и сбрасывает позицию.

        Обрабатывает разные типы file-like объектов.
        """
        file_obj = file.file

        data: bytes = file_obj.read()

        self._reset_file_position(file_obj)  # type: ignore

        if not data:
            raise ImageValidationError("Файл пуст")

        return data
```
---
## def _reset_file_position:

```python
    @staticmethod
    def _reset_file_position(file_obj: BinaryIO) -> None:
        try:
            file_obj.seek(0)
        except (OSError, io.UnsupportedOperation) as e:
            logger.debug("Не удалось сбросить позицию файла: %s", e)
```
---
## def _verify_image_format:
#### Проверяет формат изображения через PIL.

```python
    def _verify_image_format(self, image_data: bytes) -> None:
        """Проверяет формат изображения через PIL."""
        with Image.open(io.BytesIO(image_data)) as img:
            detected_format = (img.format or "").upper()

        if detected_format not in self._allowed_formats:
            allowed_str = ", ".join(sorted(self._allowed_formats))
            raise ImageExtensionValidationError(
                f"Формат изображения {detected_format} не поддерживается. "
                f"Допустимые форматы: {allowed_str}"
            )
```
---
## def _extract_extension:
#### Извлекает расширение из имени файла.

```python
    @staticmethod
    def _extract_extension(filename: str) -> str:
        """Извлекает расширение из имени файла."""
        _, ext = os.path.splitext(filename)
        return ext.lower().lstrip(".")
```
---