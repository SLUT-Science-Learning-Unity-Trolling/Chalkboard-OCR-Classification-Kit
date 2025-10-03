class PasswordDontMatch(Exception):
    """Исключение, возникающее при несовпадении паролей."""

    def __init__(
        self, message: str | Exception = "Пароли не совпадают."
    ) -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
        """
        self.message: str | Exception = message


class EmailValidationError(Exception):
    """Исключение, возникающее при невалидном email."""

    def __init__(
        self, message: str | Exception = "Введите корректный email."
    ) -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
        """
        self.message: str | Exception = message


class EmailAlreadyTaken(Exception):
    """Исключение, возникающее при зарегистрированном email."""

    def __init__(
        self, message: str | Exception = "Email уже зарегистрирован."
    ) -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
        """
        self.message: str | Exception = message


class InvalidEmailOrPassword(Exception):
    """Исключение, возникающее при невалидном логине или пароле."""

    def __init__(
        self, message: str | Exception = "Неверный логин или пароль."
    ) -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
        """
        self.message: str | Exception = message
