# Модуль user

Модуль, содержащий исключения для сервиса пользователей.

## Класс UserCreationError

**Исключение, возникающее при ошибке создания пользователя.**

---
## def init:
#### Конструктор.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `message` | `str | Exception` | Сообщение об ошибке. |

```python
    def __init__(self, message: str | Exception) -> None:
        """Конструктор.

        Args:
            message (str | Exception): Сообщение об ошибке.
        """
        super().__init__(message)
        self.message: str | Exception = message
```
---
## Класс ImageUploadError

**Исключение, возникающее при ошибке загрузки изображения.**

---
## def init:
#### Конструктор.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `message` | `str | Exception` | Сообщение об ошибке. |

```python
    def __init__(self, message: str | Exception) -> None:
        """Конструктор.

        Args:
            message (str | Exception): Сообщение об ошибке.
        """
        super().__init__(message)
        self.message: str | Exception = message
```
---
## Класс AbsentUserError

**Исключение, возникающее при попытке загрузить картинку без аккаунта.**

---
## def init:
#### Конструктор.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `message` | `str | Exception` | Сообщение об ошибке. |

```python
    def __init__(self, message: str | Exception) -> None:
        """Конструктор.

        Args:
            message (str | Exception): Сообщение об ошибке.
        """
        super().__init__(message)
        self.message: str | Exception = message
```
---
## Класс GetImagesError

**Исключение, возникающее при ошибке получения картинок.**

---
## def init:
#### Конструктор.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `message` | `str | Exception` | Сообщение об ошибке. |

```python
    def __init__(self, message: str | Exception) -> None:
        """Конструктор.

        Args:
            message (str | Exception): Сообщение об ошибке.
        """
        super().__init__(message)
        self.message: str | Exception = message
```
---
## Класс DeleteImageError

**Исключение, возникающее при ошибке удаления картинки.**

---
## def init:
#### Конструктор.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `message` | `str | Exception` | Сообщение об ошибке. |

```python
    def __init__(self, message: str | Exception) -> None:
        """Конструктор.

        Args:
            message (str | Exception): Сообщение об ошибке.
        """
        super().__init__(message)
        self.message: str | Exception = message
```
---