"""Модуль, содержащий исключения для сервиса безопасности."""
# SecurityErrors


class TooManyRequestsError(Exception):
    """Исключение, возникающее при превышении лимита запросов."""

    def __init__(
        self,
        message: str | Exception = "Превышен лимит запросов.",
        retry_after: int | None = None,
    ) -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
            retry_after (int | None, optional): Время ожидания перед повторным запросом.
        """
        super().__init__(message)
        self.message = message
        self.retry_after = retry_after


class InvalidTokenError(Exception):
    """Исключение, возникающее при невалидном токене."""

    def __init__(self, message: str | Exception = "Сессия не действительна.") -> None:
        """Конструктор.

        Args:
            message (str | Exception, optional): Сообщение об ошибке".
        """
        super().__init__(message)
        self.message: str | Exception = message
