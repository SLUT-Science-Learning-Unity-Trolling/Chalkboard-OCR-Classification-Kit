# -*- coding: utf-8 -*-
# ValidationErrors


class PasswordValidationError(Exception):
    """Исключение, возникающее при невалидном пароле."""

    def __init__(self, message: str | Exception = "Пароль не валиден") -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
        """
        self.message: str | Exception = message


class UsernameValidationError(Exception):
    """Исключение, возникающее при невалидном пароле."""

    def __init__(self, message: str | Exception = "Логин не валиден") -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
        """
        self.message: str | Exception = message
