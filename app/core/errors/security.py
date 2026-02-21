"""Модуль, содержащий исключения для сервиса безопасности."""
# SecurityErrors


class TooManyRequestsError(Exception):
    """Исключение, возникающее при превышении лимита запросов."""

    def __init__(self, message: str | Exception = "Превышен лимит запросов.") -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
        """
        super().__init__(message)
        self.message: str | Exception = message
