"""Модуль содержит интерфейс для работы с S3 совместимыми хранилищами."""
# S3Interface

from abc import ABC, abstractmethod


class S3Interface(ABC):
    """Интерфейс для работы с S3 совместимыми хранилищами."""

    @abstractmethod
    def upload_file(self, file_path: str, object_name: str) -> None:
        """Загрузка файла в хранилище.

        Args:
          file_path (str): Локальный путь к файлу.
          object_name (str): Имя объекта в хранилище.
        """
        raise NotImplementedError

    @abstractmethod
    def download_file(self, object_name: str, file_path: str) -> None:
        """Скачивание файла из хранилища.

        Args:
          object_name (str): Имя объекта в хранилище.
          file_path (str): Локальный путь для сохранения файла.
        """
        raise NotImplementedError

    @abstractmethod
    def delete_file(self, object_name: str) -> None:
        """Удаление файла из хранилища.

        Args:
          object_name (str): Имя объекта в хранилище.
        """
        raise NotImplementedError

    @abstractmethod
    def generate_presigned_url(self, object_name: str, expiration: int = 3600) -> str:
        """Генерация временной ссылки для доступа к файлу.

        Args:
          object_name (str): Имя объекта в хранилище.
          expiration (int): Время действия ссылки в секундах. По умолчанию 3600 секунд (1 час).

        Returns:
          str: Временная ссылка для доступа к файлу.
        """
        raise NotImplementedError
