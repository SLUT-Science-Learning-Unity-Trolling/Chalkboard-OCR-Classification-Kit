## Класс ValidationService

**Сервис валидации.**

---
## init:
#### Инциализация.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `config` | `Config` | Конфиг |

```python
    def __init__(self, config=config.Config) -> None:  # type: ignore
        """Инциализация.

        Args:
            config (Config): Конфиг
        """
        self.config = config
```
---
## validate_password:
#### Валидатор паролей, настройки берутся из конфига.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `password` | `str` | Пароль для валидации |

#### Возвращает
| Тип | Описание |
|-----|----------|
| `bool` | True, если пароль валиден |

#### Исключения
| Исключение | Описание |
|------------|----------|
| `PasswordValidationError` | Ошибка при валидации пароля |

```python
    async def validate_password(self, password: str) -> bool:
        """Валидатор паролей, настройки берутся из конфига.

        Args:
            password (str): Пароль для валидации

        Raises:
            PasswordValidationError: Ошибка при валидации пароля

        Returns:
            bool: True, если пароль валиден
        """
        if len(password) < self.config.PASSWORD_MIN_LENGTH:
            raise PasswordValidationError(
                f"Пароль должен быть минимум {self.config.PASSWORD_MIN_LENGTH} символов."
            )

        if not any(char.isdigit() for char in password):
            raise PasswordValidationError(
                "Пароль должен содержать хотя бы одну цифру."
            )

        if not any(char.isupper() for char in password):
            raise PasswordValidationError(
                "Пароль должен содержать хотя бы одну заглавную букву."
            )

        if not any(char.islower() for char in password):
            raise PasswordValidationError(
                "Пароль должен содержать хотя бы одну строчную букву."
            )

        if not any(
            char in self.config.PASSWORD_SPEC_SYMBOLS for char in password
        ):
            raise PasswordValidationError(
                f"Пароль должен содержать хотя бы один спец. символ из {self.config.PASSWORD_SPEC_SYMBOLS}."
            )

        return True
```
---
## validate_username:
#### Проверка имени пользователя.
Требования:
- Минимальная длина: self.config.USERNAME_MIN_LENGTH
- Максимальная длина: self.config.USERNAME_MAX_LENGTH
- Разрешены только латинские буквы, цифры, символы _ и -

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `username` | `str` | Имя пользователя |

#### Возвращает
| Тип | Описание |
|-----|----------|
| `bool` | True, если имя пользователя валидно |

#### Исключения
| Исключение | Описание |
|------------|----------|
| `UsernameValidationError` | Ошибка при валидации имени |

```python
    async def validate_username(self, username: str) -> bool:
        """Проверка имени пользователя.

        Требования:
        - Минимальная длина: self.config.USERNAME_MIN_LENGTH
        - Максимальная длина: self.config.USERNAME_MAX_LENGTH
        - Разрешены только латинские буквы, цифры, символы _ и -

        Args:
            username (str): Имя пользователя

        Returns:
            bool: True, если имя пользователя валидно

        Raises:
            UsernameValidationError: Ошибка при валидации имени
        """
        if len(username) < self.config.USERNAME_MIN_LENGTH:
            raise UsernameValidationError(
                f"Имя пользователя должно быть не короче {self.config.USERNAME_MIN_LENGTH} символов."
            )

        if len(username) > self.config.USERNAME_MAX_LENGTH:
            raise UsernameValidationError(
                f"Имя пользователя не должно превышать {self.config.USERNAME_MAX_LENGTH} символов."
            )

        if not re.match(r"^[A-Za-z0-9_-]+$", username):
            raise UsernameValidationError(
                "Имя пользователя может содержать только латинские буквы, цифры, символы '_' и '-'."
            )

        return True
```
---