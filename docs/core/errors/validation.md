# Модуль validation

Модуль, содержащий исключения для сервиса валидации.

## Класс PasswordValidationError

**Исключение, возникающее при невалидном пароле.**

```python
class PasswordValidationError(Exception):
    """Исключение, возникающее при невалидном пароле."""
```

---
## def init:
#### Конструктор.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `message` | `str \| Exception` | Сообщение об ошибке". (optional) |

```python
    def __init__(self, message: str | Exception = "Пароль не валиден") -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
        """
        super().__init__(message)
        self.message: str | Exception = message
```
---
## Класс UsernameValidationError

**Исключение, возникающее при невалидном логине.**

```python
class UsernameValidationError(Exception):
    """Исключение, возникающее при невалидном логине."""
```

---
## def init:
#### Конструктор.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `message` | `str \| Exception` | Сообщение об ошибке". (optional) |

```python
    def __init__(self, message: str | Exception = "Логин не валиден") -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
        """
        super().__init__(message)
        self.message: str | Exception = message
```
---
## Класс ImageExtensionValidationError

**Исключение, возникающее при невалидном расширении картинки.**

```python
class ImageExtensionValidationError(Exception):
    """Исключение, возникающее при невалидном расширении картинки."""
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
        self,
        message: str
        | Exception = "Расширение должно быть одним из списка: .jpg, .jpeg, .png, .tif, .tiff",
    ) -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
        """
        super().__init__(message)
        self.message: str | Exception = message
```
---
## Класс ImageValidationError

**Исключение, возникающее при ошибке при валидации изображения.**

```python
class ImageValidationError(Exception):
    """Исключение, возникающее при ошибке при валидации изображения."""
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
        self,
        message: str | Exception = "Ошибка валидации изображения",
    ) -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
        """
        super().__init__(message)
        self.message: str | Exception = message
```
---
## Класс ImageNotFoundError

**Исключение, возникающее при невалидном расширении картинки.**

```python
class ImageNotFoundError(Exception):
    """Исключение, возникающее при невалидном расширении картинки."""
```

---
## def init:
#### Конструктор.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `message` | `str \| Exception` | Сообщение об ошибке". (optional) |

```python
    def __init__(self, message: str | Exception = "Картинка не найдена") -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
        """
        super().__init__(message)
        self.message: str | Exception = message
```
---
## Класс IdentificatorIsNullError

**Исключение, возникающее если email и username пустые.**

```python
class IdentificatorIsNullError(Exception):
    """Исключение, возникающее если email и username пустые."""
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
        self,
        message: str | Exception = "Имя пользователя или почта не должны быть пустыми",
    ) -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
        """
        super().__init__(message)
        self.message: str | Exception = message
```
---