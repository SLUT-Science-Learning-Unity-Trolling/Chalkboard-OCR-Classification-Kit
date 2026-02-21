"""Модуль, содержащий исключения для сервиса пользователей."""
# UserErrors


class UserCreationError(Exception):
    """Исключение, возникающее при ошибке создания пользователя."""

    def __init__(self, message: str | Exception) -> None:
        """Конструктор.

        Args:
            message (str | Exception): Сообщение об ошибке.
        """
        super().__init__(message)
        self.message: str | Exception = message


class ImageUploadError(Exception):
    """Исключение, возникающее при ошибке загрузки изображения."""

    def __init__(self, message: str | Exception) -> None:
        """Конструктор.

        Args:
            message (str | Exception): Сообщение об ошибке.
        """
        super().__init__(message)
        self.message: str | Exception = message


class AbsentUserError(Exception):
    """Исключение, возникающее при попытке загрузить картинку без аккаунта."""

    def __init__(self, message: str | Exception) -> None:
        """Конструктор.

        Args:
            message (str | Exception): Сообщение об ошибке.
        """
        super().__init__(message)
        self.message: str | Exception = message


class GetImagesError(Exception):
    """Исключение, возникающее при ошибке получения картинок."""

    def __init__(self, message: str | Exception) -> None:
        """Конструктор.

        Args:
            message (str | Exception): Сообщение об ошибке.
        """
        super().__init__(message)
        self.message: str | Exception = message


class DeleteImageError(Exception):
    """Исключение, возникающее при ошибке удаления картинки."""

    def __init__(self, message: str | Exception) -> None:
        """Конструктор.

        Args:
            message (str | Exception): Сообщение об ошибке.
        """
        super().__init__(message)
        self.message: str | Exception = message
