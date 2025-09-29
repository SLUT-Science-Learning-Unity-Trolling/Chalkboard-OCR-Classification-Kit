from typing import Optional

from pymongo import AsyncMongoClient

from app.config import Config


class MongoGateway:
    def __init__(self):
        self._uri = Config.DATABASE_URL
        self._database = Config.DATABASE_NAME
        self._username = Config.DATABASE_USER
        self._password = Config.DATABASE_PASSWORD
        self._client: Optional[AsyncMongoClient] = None

        if not self._uri:
            raise ValueError("DATABASE_URL is not set in configuration")

    async def connect(self) -> None:
        """Устанавливает соединение с MongoDB."""
        try:
            self._client = AsyncMongoClient(self._uri)
            await self._client.admin.command("ping")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to MongoDB: {str(e)}")

    async def get_database(self):
        """Возвращает объект базы данных."""
        if not self._client:
            await self.connect()
        return self._client[self._database]

    async def get_collection(self, name: str):
        """Возвращает коллекцию по имени."""
        db = await self.get_database()
        return db[name]

    async def close(self):
        """Закрывает соединение с MongoDB."""
        if self._client:
            self._client.close()
