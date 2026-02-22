"""Модуль содержит доменную модель пользователя."""

# UserDE
from dataclasses import dataclass

from bson import ObjectId


@dataclass
class User:
    """Доменная модель пользователя.

    Attributes:
        _id (ObjectId): Уникальный идентификатор пользователя
        username (str): Имя пользователя
        email (str): Email пользователя
        password_hash (str): Хэш пароля
    """

    _id: ObjectId
    username: str
    email: str
    password_hash: str

    @property
    def id(self) -> str:
        """Возвращает строковое представление ID.

        Returns:
            str: Уникальный идентификатор пользователя
        """
        return str(self._id)
