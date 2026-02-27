"""Модуль, содержащий исключения для сервиса валидации."""
# ValidationErrors


class PasswordValidationError(Exception):
    """Исключение, возникающее при невалидном пароле."""

    def __init__(self, message: str | Exception = "Пароль не валиден") -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
        """
        super().__init__(message)
        self.message: str | Exception = message


class UsernameValidationError(Exception):
    """Исключение, возникающее при невалидном логине."""

    def __init__(self, message: str | Exception = "Логин не валиден") -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
        """
        super().__init__(message)
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
        super().__init__(message)
        self.message: str | Exception = message


class ImageValidationError(Exception):
    """Исключение, возникающее при ошибке при валидации изображения."""

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


class ImageNotFoundError(Exception):
    """Исключение, возникающее при невалидном расширении картинки."""

    def __init__(self, message: str | Exception = "Картинка не найдена") -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
        """
        super().__init__(message)
        self.message: str | Exception = message


class IdentificatorIsNullError(Exception):
    """Исключение, возникающее если email и username пустые."""

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
