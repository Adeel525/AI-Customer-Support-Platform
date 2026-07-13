from fastapi import HTTPException, status

from app.repositories.chatbot_repository import ChatbotRepository


class ChatbotService:
    def __init__(self, db, workspace_id: str):
        self.workspace_id = workspace_id
        self.repo = ChatbotRepository(db, workspace_id)

    async def create(self, data: dict) -> dict:
        return await self.repo.create({
            "name": data["name"],
            "welcome_message": data.get("welcome_message", "Hi! How can I help you today?"),
            "primary_color": data.get("primary_color", "#6366f1"),
            "theme": data.get("theme", "light"),
            "language": data.get("language", "en"),
            "tone": data.get("tone", "professional"),
            "personality": data.get("personality", "support"),
            "avatar_url": data.get("avatar_url"),
            "document_ids": data.get("document_ids", []),
            "is_active": True,
        })

    async def get(self, chatbot_id: str) -> dict:
        bot = await self.repo.get_by_id(chatbot_id)
        if not bot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot not found")
        return bot

    async def list(self, skip: int = 0, limit: int = 50) -> tuple[list, int]:
        return await self.repo.list(skip=skip, limit=limit)

    async def update(self, chatbot_id: str, data: dict) -> dict:
        await self.get(chatbot_id)
        update_data = {k: v for k, v in data.items() if v is not None}
        return await self.repo.update(chatbot_id, update_data)

    async def delete(self, chatbot_id: str) -> bool:
        await self.get(chatbot_id)
        return await self.repo.delete(chatbot_id)

    async def get_public(self, chatbot_id: str) -> dict:
        bot = await self.repo.get_public(chatbot_id)
        if not bot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot not found")
        return bot
