from jam import utils


class SecurityService:
    """Секьюрити сервис для работы с сессиями и т.п."""

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
