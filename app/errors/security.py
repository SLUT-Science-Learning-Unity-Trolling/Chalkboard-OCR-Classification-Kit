class PasswordValidationError(Exception):
    def __init__(self, message: str | Exception = "Пароль не валиден") -> None:
        self.message: str | Exception = message
