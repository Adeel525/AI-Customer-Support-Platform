from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase


class UserRepository:
    collection_name = "users"

    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db[self.collection_name]

    def _serialize(self, doc: dict[str, Any] | None) -> dict[str, Any] | None:
        if not doc:
            return None
        doc["id"] = str(doc.pop("_id"))
        doc.pop("password_hash", None)
        return doc

    async def get_by_id(self, user_id: str) -> dict[str, Any] | None:
        from bson import ObjectId
        doc = await self.collection.find_one({"_id": ObjectId(user_id)})
        return self._serialize(doc)

    async def get_by_email(self, email: str) -> dict[str, Any] | None:
        doc = await self.collection.find_one({"email": email.lower()})
        if not doc:
            return None
        doc["id"] = str(doc.pop("_id"))
        return doc

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        from datetime import datetime, timezone
        data["email"] = data["email"].lower()
        data["created_at"] = datetime.now(timezone.utc)
        data["updated_at"] = datetime.now(timezone.utc)
        result = await self.collection.insert_one(data)
        return await self.get_by_id(str(result.inserted_id))

    async def update(self, user_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        from datetime import datetime, timezone
        from bson import ObjectId
        data["updated_at"] = datetime.now(timezone.utc)
        data.pop("id", None)
        await self.collection.update_one({"_id": ObjectId(user_id)}, {"$set": data})
        return await self.get_by_id(user_id)
