from app.repositories.base import BaseRepository


class ChatbotRepository(BaseRepository):
    collection_name = "chatbots"

    async def get_public(self, chatbot_id: str) -> dict | None:
        from bson import ObjectId
        doc = await self.collection.find_one({
            "_id": ObjectId(chatbot_id),
            "is_active": True,
        })
        return self._serialize(doc)
