"""Модуль, содержащий исключения для сервиса валидации."""
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
    """Исключение, возникающее при невалидном логине."""

    def __init__(self, message: str | Exception = "Логин не валиден") -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
        """
        self.message: str | Exception = message


class ImageExtensionValidationError(Exception):
    """Исключение, возникающее при невалидном расширении картинки."""

    def __init__(
        self,
        message: str
        | Exception = "Расширение должно быть одним из списка: .jpg, .jpeg, .png, .tif, .tiff",
    ) -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
        """
        self.message: str | Exception = message


class ImageNotFoundError(Exception):
    """Исключение, возникающее при невалидном расширении картинки."""

    def __init__(self, message: str | Exception = "Картинка не найдена") -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
        """
        self.message: str | Exception = message
