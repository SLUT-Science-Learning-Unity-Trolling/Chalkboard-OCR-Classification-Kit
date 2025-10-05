# -*- coding: utf-8 -*-
# UserDE
from dataclasses import dataclass

from bson import ObjectId


@dataclass
class User:
    """Доменная модель пользователя.

    Args:
        _id: Уникальный идентификатор пользователя
        username: Имя пользователя
        email: Email пользователя
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
