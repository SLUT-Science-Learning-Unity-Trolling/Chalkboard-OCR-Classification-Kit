from motor.motor_asyncio import AsyncIOMotorClient


class MongoGateway:
    def __init__(
        self, uri: str = "mongodb://localhost:27017", db_name: str = "db"
    ) -> None:
        self._client = AsyncIOMotorClient(uri)
        self._db = self._client[db_name]

    async def get_collection(self, collection: str):
        return self._db[collection]
