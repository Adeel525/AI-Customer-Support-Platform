from app.repositories.base import BaseRepository


class ApiKeyRepository(BaseRepository):
    collection_name = "api_keys"

    async def get_by_hash(self, key_hash: str) -> dict | None:
        doc = await self.collection.find_one({"key_hash": key_hash})
        return self._serialize(doc)
