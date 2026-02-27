"""Модуль содержит модели данных для токенов."""
# token.py

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, slots=True)
class TokenClaims:
    """Представляет набор базовых claims (утверждений) для PASETO токена.

    Этот класс описывает информацию, которую содержит токен для идентификации
    пользователя и определения типа токена (access или refresh).

    Attributes:
        sub (str): Уникальный идентификатор субъекта (пользователя).
        type (Literal["access", "refresh"]): Тип токена.
        jti (str): Уникальный идентификатор токена (JWT ID / Token ID).
        username (str | None, optional): Имя пользователя, связанное с токеном.
        email (str | None, optional): Email пользователя, связанный с токеном.
    """

    sub: str
    type: Literal["access", "refresh"]
    jti: str
    username: str | None = None
    email: str | None = None
