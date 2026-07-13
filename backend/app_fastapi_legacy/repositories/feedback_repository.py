from motor.motor_asyncio import AsyncIOMotorDatabase


class FeedbackRepository:
    collection_name = "feedback"

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

    async def get_csat_stats(self, workspace_id: str) -> dict:
        pipeline = [
            {"$match": {"workspace_id": workspace_id}},
            {"$group": {
                "_id": None,
                "avg_rating": {"$avg": "$rating"},
                "total": {"$sum": 1},
                "positive": {"$sum": {"$cond": [{"$gte": ["$rating", 4]}, 1, 0]}},
            }},
        ]
        result = await self.collection.aggregate(pipeline).to_list(1)
        if result:
            r = result[0]
            return {
                "avg_rating": round(r.get("avg_rating", 0), 2),
                "total": r.get("total", 0),
                "csat_score": round(r.get("positive", 0) / max(r.get("total", 1), 1) * 100, 1),
            }
        return {"avg_rating": 0, "total": 0, "csat_score": 0}
