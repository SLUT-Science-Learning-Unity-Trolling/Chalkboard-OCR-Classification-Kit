class PasswordDontMatch(Exception):
    def __init__(
        self, message: str | Exception = "Пароли не совпадают."
    ) -> None:
        self.message: str | Exception = message


class EmailValidationError(Exception):
    def __init__(
        self, message: str | Exception = "Введите корректный email."
    ) -> None:
        self.message: str | Exception = message


class EmailAlreadyTaken(Exception):
    def __init__(
        self, message: str | Exception = "Email уже зарегистрирован."
    ) -> None:
        self.message: str | Exception = message
