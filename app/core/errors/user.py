"""Модуль, содержащий исключения для сервиса пользователей."""
# UserErrors


class UserCreationError(Exception):
    """Исключение, возникающее при ошибке создания пользователя."""

    def __init__(self, message: str | Exception) -> None:
        """Конструктор.

        Args:
            message (str | Exception): Сообщение об ошибке.
        """
        self.message: str | Exception = message
