from jam import utils

from app.errors.security import PasswordValidationError

from ... import config


class SecurityService:

    min_length = config.Config.PASSWORD_MIN_LENGTH
    spec_symbols = config.Config.PASSWORD_SPEC_SYMBOLS

    def __init__(self):
        pass

    async def validate_password(self, password: str) -> bool:
        """
        Валидатор паролей, настройки берутся из конфига

        Args:
            password (str): Пароль для валидации

        Raises:
            PasswordValidationError: Ошибка при валидации пароля

        Returns:
            bool: True, если пароль валиден
        """
        if len(password) < self.min_length:
            raise PasswordValidationError(
                f"Пароль должен быть минимум {self.min_length} символов."
            )

        if not any(char.isdigit() for char in password):
            raise PasswordValidationError(
                "Пароль должен содержать хотя бы одну цифру."
            )

        if not any(char.isupper() for char in password):
            raise PasswordValidationError(
                "Пароль должен содержать хотя бы одну заглавную букву."
            )

        if not any(char.islower() for char in password):
            raise PasswordValidationError(
                "Пароль должен содержать хотя бы одну строчную букву."
            )

        if not any(char in self.spec_symbols for char in password):
            raise PasswordValidationError(
                f"Пароль должен содержать хотя бы один спец. символ из {self.spec_symbols}."
            )

        return True

    def hash_password(self, password: str) -> tuple[str, str]:
        return utils.hash_password(password, salt_size=36)

    def serialize_hash(self, salt: str, _hash: str) -> str:
        return utils.serialize_hash(salt, _hash)
