from jam import utils

from app import config
from app.errors.security import PasswordValidationError


class SecurityService:
    """Секьюрити сервис для работы с паролями, сессиями и т.п."""

    def __init__(self, config=config.Config) -> None:  # type: ignore
        """Конструктор.

        Args:
            config (Config): Конфиг
        """
        self.config = config

    async def validate_password(self, password: str) -> bool:
        """Валидатор паролей, настройки берутся из конфига.

        Args:
            password (str): Пароль для валидации

        Raises:
            PasswordValidationError: Ошибка при валидации пароля

        Returns:
            bool: True, если пароль валиден
        """
        if len(password) < self.config.PASSWORD_MIN_LENGTH:
            raise PasswordValidationError(
                f"Пароль должен быть минимум {self.config.PASSWORD_MIN_LENGTH} символов."
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

        if not any(
            char in self.config.PASSWORD_SPEC_SYMBOLS for char in password
        ):
            raise PasswordValidationError(
                f"Пароль должен содержать хотя бы один спец. символ из {self.config.PASSWORD_SPEC_SYMBOLS}."
            )

        return True

    def hash_password(self, password: str) -> tuple[str, str]:
        """Функция хэширования пароля."""
        return utils.hash_password(password, salt_size=36)

    def serialize_hash(self, salt: str, hash_: str) -> str:
        """Функция сериализации хэша пароля."""
        return utils.serialize_hash(salt, hash_)

    def deserialize_hash(self, data: str) -> tuple[str, str]:
        """Функция десериализации хэша пароля."""
        return utils.deserialize_hash(data)

    def verify_hash(self, password: str, salt: str, hash_: str) -> bool:
        """Функция проверки хэша пароля."""
        return utils.check_password(password, hash_, salt)
