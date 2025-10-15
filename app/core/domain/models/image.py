"""Модуль содержит доменную модель загруженного изображения."""
# UploadedImage

from dataclasses import dataclass

from bson import ObjectId


@dataclass
class UploadedImage:
    """Доменная модель загруженного изображения.

    Args:
        _id: Уникальный идентификатор изображения
        user_id: Уникальный идентификатор пользователя
        url: Путь к изображению
        uploaded_at: Дата загрузки изображения
    """

    _id: ObjectId
    _user_id: ObjectId
    url: str
    uploaded_at: int

    @property
    def id(self) -> str:
        """Возвращает строковое представление ID.

        Returns:
            str: Уникальный идентификатор картинки
        """
        return str(self._id)

    @property
    def user_id(self) -> str:
        """Возвращает строковое представление ID.

        Returns:
            str: Уникальный идентификатор пользователя
        """
        return str(self.user_id)
