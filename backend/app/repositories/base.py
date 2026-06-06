from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase


class BaseRepository:
    collection_name: str = ""

    def __init__(self, db: AsyncIOMotorDatabase, workspace_id: str | None = None):
        self.db = db
        self.collection = db[self.collection_name]
        self.workspace_id = workspace_id

    def _serialize(self, doc: dict[str, Any] | None) -> dict[str, Any] | None:
        if not doc:
            return None
        doc["id"] = str(doc.pop("_id"))
        return doc

    def _serialize_many(self, docs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [self._serialize(doc) for doc in docs if doc]

    def _base_filter(self, extra: dict[str, Any] | None = None) -> dict[str, Any]:
        filt: dict[str, Any] = {}
        if self.workspace_id:
            filt["workspace_id"] = self.workspace_id
        if extra:
            filt.update(extra)
        return filt

    async def get_by_id(self, id: str) -> dict[str, Any] | None:
        doc = await self.collection.find_one(self._base_filter({"_id": ObjectId(id)}))
        return self._serialize(doc)

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        data["created_at"] = now
        data["updated_at"] = now
        if self.workspace_id and "workspace_id" not in data:
            data["workspace_id"] = self.workspace_id
        result = await self.collection.insert_one(data)
        return await self.get_by_id(str(result.inserted_id))

    async def update(self, id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        data["updated_at"] = datetime.now(timezone.utc)
        data.pop("id", None)
        data.pop("_id", None)
        await self.collection.update_one(
            self._base_filter({"_id": ObjectId(id)}),
            {"$set": data},
        )
        return await self.get_by_id(id)

    async def delete(self, id: str) -> bool:
        result = await self.collection.delete_one(
            self._base_filter({"_id": ObjectId(id)})
        )
        return result.deleted_count > 0

    async def list(
        self,
        skip: int = 0,
        limit: int = 50,
        extra_filter: dict[str, Any] | None = None,
        sort: list[tuple[str, int]] | None = None,
    ) -> tuple[list[dict[str, Any]], int]:
        filt = self._base_filter(extra_filter)
        total = await self.collection.count_documents(filt)
        cursor = self.collection.find(filt)
        if sort:
            cursor = cursor.sort(sort)
        docs = await cursor.skip(skip).limit(limit).to_list(limit)
        return self._serialize_many(docs), total
