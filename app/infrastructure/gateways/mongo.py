from pymongo import AsyncMongoClient


class MongoGateway:
    def __init__(
        self, uri: str = "mongodb://localhost:27017", db_name: str = "db"
    ) -> None:
        self.client = AsyncMongoClient(uri)
        self.db = self.client[db_name]

    async def get_connection(self):
        """Создание асинхронного коннекшена."""
        return await self.client.aconnect()

    async def close(self):
        """Закрывает соединение с MongoDB."""
        await self.client.close()

    async def get_collection(self, collection_name: str):
        return self.db[collection_name]
