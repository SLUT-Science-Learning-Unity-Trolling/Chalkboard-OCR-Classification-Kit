from dataclasses import dataclass
from typing import Union
from uuid import UUID


@dataclass
class User:
    """Доменная модель пользователя.

    Attributes:
        _id: Уникальный идентификатор пользователя
        username: Имя пользователя
        email: Email пользователя
    """

    _id: Union[str, UUID]
    username: str
    email: str
    password_hash: str

    @property
    def id(self) -> str:
        """Возвращает строковое представление ID."""
        return str(self._id)
