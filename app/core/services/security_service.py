"""Модуль содержит класс SecurityService для работы с хэшированием паролей."""
# SecurityService

from jam import utils


class SecurityService:
    """Секьюрити сервис для работы с сессиями и т.п."""

    def hash_password(self, password: str) -> tuple[str, str]:
        """Функция хэширования пароля.

        Args:
            password (str): Пароль

        Returns:
            tuple[str, str]: salt, hash
        """
        return utils.hash_password(password, salt_size=36)

    def serialize_hash(self, salt: str, hash_: str) -> str:
        """Функция сериализации хэша пароля.

        Args:
            salt (str): Соль
            hash_ (str): Хэш

        Returns:
            str: сериализованный хэш
        """
        return utils.serialize_hash(salt, hash_)

    def deserialize_hash(self, data: str) -> tuple[str, str]:
        """Функция десериализации хэша пароля.

        Args:
            data (str): Сериализованный хэш

        Returns:
            tuple[str, str]: salt, hash
        """
        return utils.deserialize_hash(data)

    def verify_hash(self, password: str, salt: str, hash_: str) -> bool:
        """Функция проверки хэша пароля.

        Args:
            password (str): Пароль
            salt (str): Соль
            hash_ (str): Хэш

        Returns:
            bool: True, если пароль верен
        """
        return utils.check_password(password, hash_, salt)
