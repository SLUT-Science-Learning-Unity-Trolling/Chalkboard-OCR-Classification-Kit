class UserCreationError(Exception):
    """Исключение, возникающее при ошибке создания пользователя."""

    def __init__(self, message: str | Exception) -> None:
        self.message: str | Exception = message
