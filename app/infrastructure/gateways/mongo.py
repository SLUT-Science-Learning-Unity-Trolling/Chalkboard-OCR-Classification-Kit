from pymongo import AsyncMongoClient


class MongoGateway:
    def __init__(
        self, uri: str = "mongodb://localhost:27017", db_name: str = "db"
    ) -> None:
        self.client = AsyncMongoClient(uri)
        self.db = self._client[db_name]

    @property
    async def get_connection(self) -> None:
        """Создание асинхронного коннекшена."""
        await self.client.aconnect()
        return None

    async def get_collection(self, collection_name: str):
        return self.db[collection_name]
