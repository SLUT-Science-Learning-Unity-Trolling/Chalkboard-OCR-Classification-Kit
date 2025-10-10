"""Модуль содержит класс MongoGateway для подключения к базе данных MongoDB."""
# MongoGateway

from pymongo import AsyncMongoClient
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.database import Database

from app.config import Config


class MongoGateway:
    """Класс для работы с MongoDB."""

    def __init__(self) -> None:
        """Конструктор.

        Args:
            self._uri (str): Строка подключения к базе данных.
            self._database (str): Имя базы данных.
            self._username (str): Имя пользователя базы данных.
            self._password (str): Пароль пользователя базы данных.
            self._client (Optional[AsyncMongoClient]): Объект клиента MongoDB.

        Raises:
            ValueError: Если DATABASE_URL не установлен в конфигурации.
        """
        self._uri = Config.DATABASE_URL
        self._database = Config.DATABASE_NAME
        self._username = Config.DATABASE_USER
        self._password = Config.DATABASE_PASSWORD
        self._client: AsyncMongoClient | None = None

        if not self._uri:
            raise ValueError("DATABASE_URL is not set in configuration")

    async def connect(self) -> None:
        """Устанавливает соединение с MongoDB."""
        try:
            self._client = AsyncMongoClient(self._uri)
            await self._client.admin.command("ping")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to MongoDB: {str(e)}") from e

    async def get_database(self) -> Database:
        """Возвращает объект базы данных."""
        if not self._client:
            await self.connect()
        return self._client[self._database]  # type: ignore

    async def get_collection(self, name: str) -> AsyncCollection:
        """Возвращает коллекцию по имени."""
        db = await self.get_database()
        return db[name]

    async def close(self) -> None:
        """Закрывает соединение с MongoDB."""
        if self._client:
            self._client.close()
