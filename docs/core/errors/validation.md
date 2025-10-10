# Модуль validation

Модуль, содержащий исключения для сервиса валидации.

## Класс PasswordValidationError

**Исключение, возникающее при невалидном пароле.**

---
## def init:
#### Конструктор.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `message` | `str | Exception, optional` | Сообщение об ошибке". |

```python
    def __init__(self, message: str | Exception = "Пароль не валиден") -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
        """
        self.message: str | Exception = message
```
---
## Класс UsernameValidationError

**Исключение, возникающее при невалидном пароле.**

---
## def init:
#### Конструктор.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `message` | `str | Exception, optional` | Сообщение об ошибке". |

```python
    def __init__(self, message: str | Exception = "Логин не валиден") -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
        """
        self.message: str | Exception = message
```
---