## Класс PasswordDontMatch

**Исключение, возникающее при несовпадении паролей.**

---
### init
**Конструктор.**

**Args:**
- `message (str | Exception, optional)`: Сообщение об ошибке".

```python
    def __init__(
        self, message: str | Exception = "Пароли не совпадают."
    ) -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
        """
        self.message: str | Exception = message
```
---
## Класс EmailValidationError

**Исключение, возникающее при невалидном email.**

---
### init
**Конструктор.**

**Args:**
- `message (str | Exception, optional)`: Сообщение об ошибке".

```python
    def __init__(
        self, message: str | Exception = "Введите корректный email."
    ) -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
        """
        self.message: str | Exception = message
```
---
## Класс EmailAlreadyTaken

**Исключение, возникающее при зарегистрированном email.**

---
### init
**Конструктор.**

**Args:**
- `message (str | Exception, optional)`: Сообщение об ошибке".

```python
    def __init__(
        self, message: str | Exception = "Email уже зарегистрирован."
    ) -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
        """
        self.message: str | Exception = message
```
---
## Класс UsernameAlreadyTaken

**Исключение, возникающее при зарегистрированном email.**

---
### init
**Конструктор.**

**Args:**
- `message (str | Exception, optional)`: Сообщение об ошибке".

```python
    def __init__(
        self, message: str | Exception = "Данный логин уже зарегистрирован."
    ) -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
        """
        self.message: str | Exception = message
```
---
## Класс InvalidEmailOrPassword

**Исключение, возникающее при невалидном логине или пароле.**

---
### init
**Конструктор.**

**Args:**
- `message (str | Exception, optional)`: Сообщение об ошибке".

```python
    def __init__(
        self, message: str | Exception = "Неверный логин или пароль."
    ) -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
        """
        self.message: str | Exception = message
```
---