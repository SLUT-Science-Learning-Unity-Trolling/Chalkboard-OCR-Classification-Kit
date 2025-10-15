"""Модуль содержит DTO для работы с изображениями."""
# ImageDTO

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class UploadImageDTO:
    """Модель данных для загрузки изображения.

    Args:
        url_to_upload (str): Путь к изображению.
    """

    user_id: str
    url: str


@dataclass
class ImageDTO:
    """Модель данных для изображения.

    Args:
        user_id (str): Уникальный идентификатор пользователя.
        url (str): Путь к изображению.
    """

    id: str
    user_id: str
    url: str

    @classmethod
    def fromrow(cls, row: dict[str, Any]) -> ImageDTO:
        """Создает экземпляр класса из словаря.

        Args:
            row (dict[str, Any]): Словарь с данными пользователя

        Returns:
            ImageDTO: Экземпляр класса ImageDTO
        """
        return cls(
            id=str(row.get("_id") or row.get("id")),
            user_id=str(row.get("_user_id") or row.get("user_id")),
            url=row["url"],
        )
