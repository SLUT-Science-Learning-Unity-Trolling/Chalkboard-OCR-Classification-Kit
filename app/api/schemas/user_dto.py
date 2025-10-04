from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass
class UserCreateDTO:
    """Данные для создания пользователя."""

    username: str
    email: str
    password: str
    repeat_password: str


@dataclass
class UserDTO:
    """Данные о пользователе, возвращаемые пользователю."""

    id: str
    username: str
    email: str

    @classmethod
    def fromrow(cls, row: dict[str, Any]) -> UserDTO:
        """Создает экземпляр класса из словаря."""
        return cls(
            id=str(row.get("_id") or row.get("id")),
            username=row["username"],
            email=row["email"],
        )


@dataclass
class UserLoginDTO:
    """Данные для авторизации пользователя."""

    identifier: str
    password: str
