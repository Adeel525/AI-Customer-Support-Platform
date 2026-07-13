from motor.motor_asyncio import AsyncIOMotorDatabase


class WorkspaceMemberRepository:
    collection_name = "workspace_members"

    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db[self.collection_name]

    def _serialize(self, doc):
        if not doc:
            return None
        doc["id"] = str(doc.pop("_id"))
        return doc

    async def get_member(self, workspace_id: str, user_id: str) -> dict | None:
        doc = await self.collection.find_one({
            "workspace_id": workspace_id,
            "user_id": user_id,
        })
        return self._serialize(doc)

    async def list_by_workspace(self, workspace_id: str) -> list[dict]:
        cursor = self.collection.find({"workspace_id": workspace_id})
        docs = await cursor.to_list(100)
        return [self._serialize(d) for d in docs if d]

    async def list_by_user(self, user_id: str) -> list[dict]:
        cursor = self.collection.find({"user_id": user_id})
        docs = await cursor.to_list(100)
        return [self._serialize(d) for d in docs if d]

    async def create(self, data: dict) -> dict:
        from datetime import datetime, timezone
        data["created_at"] = datetime.now(timezone.utc)
        result = await self.collection.insert_one(data)
        doc = await self.collection.find_one({"_id": result.inserted_id})
        return self._serialize(doc)

    async def update_role(self, workspace_id: str, user_id: str, role: str) -> dict | None:
        await self.collection.update_one(
            {"workspace_id": workspace_id, "user_id": user_id},
            {"$set": {"role": role}},
        )
        return await self.get_member(workspace_id, user_id)

    async def delete(self, workspace_id: str, user_id: str) -> bool:
        result = await self.collection.delete_one({
            "workspace_id": workspace_id,
            "user_id": user_id,
        })
        return result.deleted_count > 0
