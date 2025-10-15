"""Модуль для работы с MiniO."""
# MiniO

import io

from boto3 import client
from botocore.exceptions import ClientError

from app.adapters.interfaces.s3 import S3Interface
from app.config import Config


class MinioGateway(S3Interface):
    """Класс для работы с MiniO."""

    def __init__(self) -> None:
        """Конструктор.

        Args:
          self._endpoint (str): URL-адрес сервера MiniO.
          self._access_key (str): Ключ доступа к MiniO.
          self._secret_key (str): Секретный ключ доступа к MiniO.
          self._bucket (str): Имя бакета в MiniO.
          self.connect(): Устанавливает соединение с MiniO.
        """
        self._endpoint = Config.MINIO_ENDPOINT
        self._access_key = Config.MINIO_ACCESS_KEY
        self._secret_key = Config.MINIO_SECRET_KEY
        self._bucket = Config.MINIO_BUCKET
        self.connect()

    def connect(self) -> None:
        """Устанавливает соединение с MiniO."""
        self._client = client(
            "s3",
            endpoint_url=self._endpoint,
            aws_access_key_id=self._access_key,
            aws_secret_access_key=self._secret_key,
        )

        try:
            existing_buckets = [
                b["Name"] for b in self._client.list_buckets().get("Buckets", [])
            ]
            if self._bucket not in existing_buckets:
                self._client.create_bucket(Bucket=self._bucket)
        except ClientError as e:
            raise Exception(f"Ошибка подключения к MiniO: {str(e)}") from e

    def upload_file(self, file_path: str, object_name: str) -> None:
        """Загружает файл в MiniO.

        Args:
          file_path (str): Путь к файлу для загрузки.
          object_name (str): Имя объекта в MiniO.
        """
        try:
            self._client.upload_file(file_path, self._bucket, object_name)
        except ClientError as e:
            raise Exception(f"Ошибка загрузки файла: {str(e)}") from e

    def put_object(
        self,
        object_name: str,
        data: io.BytesIO,
        size: int,
        content_type: str = "application/octet-stream",
    ) -> None:
        """Загружает объект в MinIO напрямую из потока.

        Args:
            object_name (str): Имя объекта в MiniO.
            data (io.BytesIO): Поток данных.
            size (int): Размер данных.
            content_type (str): Тип содержимого (по умолчанию "application/octet-stream").
        """
        if not self._client:
            self.connect()
        try:
            self._client.put_object(
                Bucket=self._bucket,
                Key=object_name,
                Body=data,
                ContentLength=size,
                ContentType=content_type,
            )
        except ClientError as e:
            raise Exception(f"Ошибка загрузки файла: {str(e)}") from e

    def download_file(self, object_name: str, file_path: str) -> None:
        """Скачивает файл из MiniO.

        Args:
          object_name (str): Имя объекта в MiniO.
          file_path (str): Путь к файлу для сохранения.
        """
        try:
            self._client.download_file(self._bucket, object_name, file_path)
        except ClientError as e:
            raise Exception(f"Ошибка скачивания файла: {str(e)}") from e

    def delete_file(self, object_name: str) -> None:
        """Удаляет файл из MiniO.

        Args:
            object_name (str): Имя объекта в MiniO.
        """
        try:
            self._client.delete_object(Bucket=self._bucket, Key=object_name)
        except ClientError as e:
            raise Exception(f"Ошибка удаления файла: {str(e)}") from e

    def generate_presigned_url(self, object_name: str, expiration: int = 3600) -> str:
        """Генерирует временную ссылку для доступа к файлу в MiniO.

        Args:
        object_name (str): Имя объекта в MiniO.
        expiration (int): Время действия ссылки в секундах (1 час).

        Returns:
          str: Временная ссылка для доступа к файлу.
        """
        try:
            url = self._client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self._bucket, "Key": object_name},
                ExpiresIn=expiration,
            )
            return url
        except ClientError as e:
            raise Exception(f"Ошибка генерации ссылки: {str(e)}") from e
