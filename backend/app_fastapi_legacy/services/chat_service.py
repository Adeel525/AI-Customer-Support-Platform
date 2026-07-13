import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.ai.rag_engine import RAGEngine
from app.models.enums import ConversationStatus, MessageRole
from app.repositories.chatbot_repository import ChatbotRepository
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.services.ticket_service import TicketService


class ChatService:
    def __init__(self, db, workspace_id: str):
        self.workspace_id = workspace_id
        self.conversation_repo = ConversationRepository(db, workspace_id)
        self.message_repo = MessageRepository(db)
        self.chatbot_repo = ChatbotRepository(db, workspace_id)
        self.rag = RAGEngine(db, workspace_id)
        self.db = db

    async def send_message(
        self,
        chatbot_id: str,
        message: str,
        conversation_id: str | None = None,
        customer_id: str | None = None,
    ) -> dict:
        chatbot = await self.chatbot_repo.get_public(chatbot_id)
        if not chatbot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot not found")

        if not conversation_id:
            conversation = await self.conversation_repo.create({
                "chatbot_id": chatbot_id,
                "customer_id": customer_id or str(uuid.uuid4()),
                "status": ConversationStatus.ACTIVE.value,
                "message_count": 0,
            })
            conversation_id = conversation["id"]
        else:
            conversation = await self.conversation_repo.get_by_id(conversation_id)
            if not conversation:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

        await self.message_repo.create({
            "conversation_id": conversation_id,
            "workspace_id": self.workspace_id,
            "role": MessageRole.USER.value,
            "content": message,
        })

        history = await self.message_repo.list_by_conversation(conversation_id)
        history_msgs = [{"role": m["role"], "content": m["content"]} for m in history]

        rag_result = await self.rag.query(
            message,
            chatbot_config=chatbot,
            conversation_history=history_msgs,
        )

        assistant_msg = await self.message_repo.create({
            "conversation_id": conversation_id,
            "workspace_id": self.workspace_id,
            "role": MessageRole.ASSISTANT.value,
            "content": rag_result["content"],
            "confidence": rag_result["confidence"],
            "sources": rag_result["sources"],
        })

        await self.conversation_repo.update(conversation_id, {
            "message_count": len(history) + 1,
            "last_message_at": datetime.now(timezone.utc),
            "last_confidence": rag_result["confidence"],
        })

        if rag_result["should_escalate"]:
            await self.conversation_repo.update(conversation_id, {
                "status": ConversationStatus.ESCALATED.value,
            })
            ticket_service = TicketService(self.db, self.workspace_id)
            await ticket_service.auto_create_from_conversation(
                conversation_id, message, rag_result
            )

        return {
            "conversation_id": conversation_id,
            "message_id": assistant_msg["id"],
            "content": rag_result["content"],
            "confidence": rag_result["confidence"],
            "sources": rag_result["sources"],
            "should_escalate": rag_result["should_escalate"],
        }

    async def escalate(self, conversation_id: str) -> dict:
        conversation = await self.conversation_repo.get_by_id(conversation_id)
        if not conversation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

        await self.conversation_repo.update(conversation_id, {
            "status": ConversationStatus.ESCALATED.value,
        })

        messages = await self.message_repo.list_by_conversation(conversation_id)
        last_user = next(
            (m["content"] for m in reversed(messages) if m["role"] == MessageRole.USER.value),
            "Customer requested human support",
        )

        ticket_service = TicketService(self.db, self.workspace_id)
        return await ticket_service.auto_create_from_conversation(
            conversation_id, last_user, {"confidence": 0.0, "content": ""}
        )
