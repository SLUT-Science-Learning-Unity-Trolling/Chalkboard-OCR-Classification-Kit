# Модуль auth

Модуль, содержащий исключения для сервиса аутентификации.

## Класс PasswordDontMatchError

**Исключение, возникающее при несовпадении паролей.**

```python
class PasswordDontMatchError(Exception):
    """Исключение, возникающее при несовпадении паролей."""
```

---
## def init:
#### Конструктор.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `message` | `str \| Exception` | Сообщение об ошибке". (optional) |

```python
    def __init__(self, message: str | Exception = "Пароли не совпадают.") -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
        """
        super().__init__(message)
        self.message: str | Exception = message
```
---
## Класс EmailValidationError

**Исключение, возникающее при невалидном email.**

```python
class EmailValidationError(Exception):
    """Исключение, возникающее при невалидном email."""
```

---
## def init:
#### Конструктор.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `message` | `str \| Exception` | Сообщение об ошибке". (optional) |

```python
    def __init__(self, message: str | Exception = "Введите корректный email.") -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
        """
        super().__init__(message)
        self.message: str | Exception = message
```
---
## Класс EmailAlreadyTakenError

**Исключение, возникающее при зарегистрированном email.**

```python
class EmailAlreadyTakenError(Exception):
    """Исключение, возникающее при зарегистрированном email."""
```

---
## def init:
#### Конструктор.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `message` | `str \| Exception` | Сообщение об ошибке". (optional) |

```python
    def __init__(self, message: str | Exception = "Email уже зарегистрирован.") -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
        """
        super().__init__(message)
        self.message: str | Exception = message
```
---
## Класс UsernameAlreadyTakenError

**Исключение, возникающее при зарегистрированном email.**

```python
class UsernameAlreadyTakenError(Exception):
    """Исключение, возникающее при зарегистрированном email."""
```

---
## def init:
#### Конструктор.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `message` | `str \| Exception` | Сообщение об ошибке". (optional) |

```python
    def __init__(
        self, message: str | Exception = "Данный логин уже зарегистрирован."
    ) -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
        """
        super().__init__(message)
        self.message: str | Exception = message
```
---
## Класс InvalidEmailOrPasswordError

**Исключение, возникающее при невалидном логине или пароле.**

```python
class InvalidEmailOrPasswordError(Exception):
    """Исключение, возникающее при невалидном логине или пароле."""
```

---
## def init:
#### Конструктор.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `message` | `str \| Exception` | Сообщение об ошибке". (optional) |

```python
    def __init__(self, message: str | Exception = "Неверный логин или пароль.") -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
        """
        super().__init__(message)
        self.message: str | Exception = message
```
---
## Класс UnauthorizedError

**Исключение, возникающее при неавторизованном доступе.**

```python
class UnauthorizedError(Exception):
    """Исключение, возникающее при неавторизованном доступе."""
```

---
## def init:
#### Конструктор.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `message` | `str \| Exception` | Сообщение об ошибке". (optional) |

```python
    def __init__(self, message: str | Exception = "Пользователь не авторизован.") -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
        """
        super().__init__(message)
        self.message: str | Exception = message
```
---