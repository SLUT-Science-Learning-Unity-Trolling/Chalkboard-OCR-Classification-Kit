"""Модуль, содержащий исключения для сервиса аутентификации."""
# AuthErrors


class PasswordDontMatchError(Exception):
    """Исключение, возникающее при несовпадении паролей."""

    def __init__(self, message: str | Exception = "Пароли не совпадают.") -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
        """
        super().__init__(message)
        self.message: str | Exception = message


class EmailValidationError(Exception):
    """Исключение, возникающее при невалидном email."""

    def __init__(self, message: str | Exception = "Введите корректный email.") -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
        """
        super().__init__(message)
        self.message: str | Exception = message


class EmailAlreadyTakenError(Exception):
    """Исключение, возникающее при зарегистрированном email."""

    def __init__(self, message: str | Exception = "Email уже зарегистрирован.") -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
        """
        super().__init__(message)
        self.message: str | Exception = message


class UsernameAlreadyTakenError(Exception):
    """Исключение, возникающее при зарегистрированном email."""

    def __init__(
        self, message: str | Exception = "Данный логин уже зарегистрирован."
    ) -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
        """
        super().__init__(message)
        self.message: str | Exception = message


class InvalidEmailOrPasswordError(Exception):
    """Исключение, возникающее при невалидном логине или пароле."""

    def __init__(self, message: str | Exception = "Неверный логин или пароль.") -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
        """
        super().__init__(message)
        self.message: str | Exception = message

class UnauthorizedError(Exception):
    """Исключение, возникающее при неавторизованном доступе."""

    def __init__(self, message: str | Exception = "Пользователь не авторизован.") -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
        """
        super().__init__(message)
        self.message: str | Exception = message

