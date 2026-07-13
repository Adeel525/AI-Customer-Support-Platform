from app.repositories.base import BaseRepository


class TicketRepository(BaseRepository):
    collection_name = "tickets"


class TicketCommentRepository:
    collection_name = "ticket_comments"

    def __init__(self, db):
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

    async def list_by_ticket(self, ticket_id: str) -> list[dict]:
        cursor = self.collection.find({"ticket_id": ticket_id}).sort("created_at", 1)
        docs = await cursor.to_list(200)
        return [self._serialize(d) for d in docs if d]
