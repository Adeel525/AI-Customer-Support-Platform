from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.ai.llm_client import LLMClient
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository


class ConversationService:
    def __init__(self, db, workspace_id: str):
        self.workspace_id = workspace_id
        self.conversation_repo = ConversationRepository(db, workspace_id)
        self.message_repo = MessageRepository(db)
        self.llm = LLMClient()

    async def list_conversations(self, status: str | None = None, skip: int = 0, limit: int = 50) -> tuple:
        extra = {"status": status} if status else None
        return await self.conversation_repo.list(
            skip=skip, limit=limit, extra_filter=extra, sort=[("last_message_at", -1)]
        )

    async def get_conversation(self, conversation_id: str) -> dict:
        conv = await self.conversation_repo.get_by_id(conversation_id)
        if not conv:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
        messages = await self.message_repo.list_by_conversation(conversation_id)
        return {**conv, "messages": messages}

    async def assign_agent(self, conversation_id: str, agent_id: str) -> dict:
        return await self.conversation_repo.update(conversation_id, {
            "assigned_agent_id": agent_id,
            "assigned_at": datetime.now(timezone.utc),
        })

    async def summarize_conversation(self, conversation_id: str) -> str:
        messages = await self.message_repo.list_by_conversation(conversation_id)
        if not messages:
            return ""

        conv_text = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
        summary = await self.llm.generate(
            [{"role": "user", "content": f"Summarize this support conversation in 2-3 sentences:\n{conv_text[:3000]}"}],
            temperature=0.3,
            max_tokens=200,
        )

        await self.conversation_repo.update(conversation_id, {
            "summary": summary,
            "summarized_at": datetime.now(timezone.utc),
        })
        return summary

    async def get_customer_history(self, customer_id: str) -> dict:
        cursor = self.conversation_repo.collection.find(
            self.conversation_repo._base_filter({"customer_id": customer_id})
        ).sort("created_at", -1).limit(20)
        conversations = await cursor.to_list(20)
        serialized = self.conversation_repo._serialize_many(conversations)
        return {
            "customer_id": customer_id,
            "conversations": serialized,
            "total": len(serialized),
        }
