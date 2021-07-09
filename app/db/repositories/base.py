from motor.motor_asyncio import AsyncIOMotorDatabase


class BaseRepository:
    def __init__(self, client: AsyncIOMotorDatabase) -> None:
        self._client = client

    @property
    def connection(self) -> AsyncIOMotorDatabase:
        return self._client
