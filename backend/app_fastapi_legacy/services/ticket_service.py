import json

from fastapi import HTTPException, status

from app.ai.llm_client import LLMClient
from app.ai.prompts.support import TICKET_SUMMARY_PROMPT
from app.models.enums import TicketPriority, TicketStatus
from app.repositories.message_repository import MessageRepository
from app.repositories.ticket_repository import TicketCommentRepository, TicketRepository


class TicketService:
    def __init__(self, db, workspace_id: str):
        self.workspace_id = workspace_id
        self.ticket_repo = TicketRepository(db, workspace_id)
        self.comment_repo = TicketCommentRepository(db)
        self.message_repo = MessageRepository(db)
        self.llm = LLMClient()

    async def create(self, data: dict, creator_id: str | None = None) -> dict:
        return await self.ticket_repo.create({
            "title": data["title"],
            "description": data["description"],
            "category": data.get("category", "technical"),
            "priority": data.get("priority", TicketPriority.MEDIUM.value),
            "status": TicketStatus.OPEN.value,
            "conversation_id": data.get("conversation_id"),
            "created_by": creator_id,
            "assigned_agent_id": None,
        })

    async def auto_create_from_conversation(
        self, conversation_id: str, last_message: str, rag_result: dict
    ) -> dict:
        messages = await self.message_repo.list_by_conversation(conversation_id)
        conv_text = "\n".join(f"{m['role']}: {m['content']}" for m in messages)

        ai_data = await self._generate_ticket_ai(conv_text)

        return await self.ticket_repo.create({
            "title": ai_data.get("title", f"Escalation: {last_message[:80]}"),
            "description": last_message,
            "category": ai_data.get("category", "technical"),
            "priority": ai_data.get("priority", TicketPriority.MEDIUM.value),
            "status": TicketStatus.OPEN.value,
            "conversation_id": conversation_id,
            "ai_summary": ai_data.get("summary", conv_text[:500]),
            "detected_intent": ai_data.get("detected_intent", "support_request"),
            "suggested_resolution": ai_data.get("suggested_resolution", ""),
            "confidence_at_escalation": rag_result.get("confidence", 0),
            "auto_generated": True,
        })

    async def _generate_ticket_ai(self, conversation: str) -> dict:
        prompt = TICKET_SUMMARY_PROMPT.format(conversation=conversation[:3000])
        try:
            response = await self.llm.generate(
                [{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=500,
            )
            return json.loads(response)
        except (json.JSONDecodeError, Exception):
            return {
                "title": "Customer Support Request",
                "summary": conversation[:500],
                "detected_intent": "general_support",
                "suggested_resolution": "Review conversation and respond to customer.",
                "priority": "medium",
                "category": "technical",
            }

    async def get(self, ticket_id: str) -> dict:
        ticket = await self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
        return ticket

    async def list(self, status_filter: str | None = None, skip: int = 0, limit: int = 50) -> tuple:
        extra = {"status": status_filter} if status_filter else None
        return await self.ticket_repo.list(skip=skip, limit=limit, extra_filter=extra, sort=[("created_at", -1)])

    async def update(self, ticket_id: str, data: dict) -> dict:
        await self.get(ticket_id)
        update_data = {k: v for k, v in data.items() if v is not None}
        return await self.ticket_repo.update(ticket_id, update_data)

    async def add_comment(self, ticket_id: str, content: str, author_id: str, is_internal: bool = False) -> dict:
        await self.get(ticket_id)
        return await self.comment_repo.create({
            "ticket_id": ticket_id,
            "workspace_id": self.workspace_id,
            "author_id": author_id,
            "content": content,
            "is_internal": is_internal,
        })

    async def list_comments(self, ticket_id: str) -> list:
        await self.get(ticket_id)
        return await self.comment_repo.list_by_ticket(ticket_id)
