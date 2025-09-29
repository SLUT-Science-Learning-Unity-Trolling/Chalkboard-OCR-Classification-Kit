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

    def __post_init__(self):
        if len(self.username) < 3:
            raise ValueError("Username must be at least 3 characters long")
        if "@" not in self.email:
            raise ValueError("Invalid email format")

    @property
    def id(self) -> str:
        """Возвращает строковое представление ID."""
        return str(self._id)
