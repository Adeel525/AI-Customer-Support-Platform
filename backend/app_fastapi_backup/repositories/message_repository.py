from motor.motor_asyncio import AsyncIOMotorDatabase


class MessageRepository:
    collection_name = "messages"

    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db[self.collection_name]

    def _serialize(self, doc):
        if not doc:
            return None
        doc["id"] = str(doc.pop("_id"))
        return doc

    async def create(self, data: dict) -> dict:
        from datetime import datetime, timezone
        data["created_at"] = datetime.now(timezone.utc)
        result = await self.collection.insert_one(data)
        doc = await self.collection.find_one({"_id": result.inserted_id})
        return self._serialize(doc)

    async def list_by_conversation(self, conversation_id: str, limit: int = 50) -> list[dict]:
        cursor = self.collection.find({"conversation_id": conversation_id}).sort("created_at", 1).limit(limit)
        docs = await cursor.to_list(limit)
        return [self._serialize(d) for d in docs if d]

    async def get_by_id(self, message_id: str) -> dict | None:
        from bson import ObjectId
        doc = await self.collection.find_one({"_id": ObjectId(message_id)})
        return self._serialize(doc)
