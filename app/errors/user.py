class UserCreationError(Exception):
    """Исключение, возникающее при ошибке создания пользователя."""

    def __init__(self, message: str = "Failed to create user"):
        self.message = message
        super().__init__(self.message)
