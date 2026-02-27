"""Модуль содержит схемы для работы с пользователями."""
# UserDTO

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True, kw_only=True)
class UserCreateDTO:
    """Данные для создания пользователя.

    Args:
        username: Имя пользователя
        email: Email пользователя
        password: Пароль пользователя
        repeat_password: Повтор пароля пользователя
    """

    username: str
    email: str
    password: str
    repeat_password: str


@dataclass()
class UserDTO:
    """Данные о пользователе, возвращаемые пользователю.

    Args:
        id: Уникальный идентификатор пользователя
        username: Имя пользователя
        email: Email пользователя
    """

    id: str
    username: str
    email: str

    @classmethod
    def fromrow(cls, row: dict[str, Any]) -> UserDTO:
        """Создает экземпляр класса из словаря.

        Args:
            row (dict[str, Any]): Словарь с данными пользователя

        Returns:
            UserDTO: Экземпляр класса UserDTO
        """
        return cls(
            id=str(row.get("_id") or row.get("id")),
            username=row["username"],
            email=row["email"],
        )


@dataclass(slots=True, kw_only=True)
class UserLoginDTO:
    """Данные для авторизации пользователя.

    Args:
        identifier: Email или username пользователя
        password: Пароль пользователя
    """

    identifier: str
    password: str
