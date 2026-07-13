from fastapi import APIRouter, Depends, Request

from app.core.database import get_database
from app.core.deps import Tenant, require_permission
from app.core.tenant import TenantContext
from app.middleware.rate_limit import limiter
from app.models.enums import Permission
from app.schemas.chat import ChatMessageRequest, FeedbackRequest
from app.services.chat_service import ChatService
from app.services.feedback_service import FeedbackService

router = APIRouter(tags=["Chat"])
public_router = APIRouter(prefix="/public/chat", tags=["Public Chat"])


def get_chat_service_for_public(chatbot_id: str):
    from app.repositories.chatbot_repository import ChatbotRepository
    db = get_database()
    bot = None

    async def _get():
        nonlocal bot
        repo = ChatbotRepository(db)
        bot = await repo.get_public(chatbot_id)
        if not bot:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot not found")
        return ChatService(db, bot["workspace_id"])

    return _get


@public_router.get("/{chatbot_id}/config")
async def get_chatbot_config(chatbot_id: str):
    from app.repositories.chatbot_repository import ChatbotRepository
    from fastapi import HTTPException, status
    db = get_database()
    repo = ChatbotRepository(db)
    bot = await repo.get_public(chatbot_id)
    if not bot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot not found")
    return {
        "id": bot["id"],
        "name": bot["name"],
        "welcome_message": bot["welcome_message"],
        "primary_color": bot["primary_color"],
        "theme": bot["theme"],
        "avatar_url": bot.get("avatar_url"),
    }


@public_router.post("/{chatbot_id}/message")
@limiter.limit("30/minute")
async def public_send_message(chatbot_id: str, data: ChatMessageRequest, request: "Request"):
    from app.repositories.chatbot_repository import ChatbotRepository
    from fastapi import HTTPException, status, Request
    db = get_database()
    repo = ChatbotRepository(db)
    bot = await repo.get_public(chatbot_id)
    if not bot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot not found")
    service = ChatService(db, bot["workspace_id"])
    return await service.send_message(chatbot_id, data.message, data.conversation_id, data.customer_id)


@public_router.post("/{chatbot_id}/escalate")
async def public_escalate(chatbot_id: str, conversation_id: str):
    from app.repositories.chatbot_repository import ChatbotRepository
    from fastapi import HTTPException, status
    db = get_database()
    repo = ChatbotRepository(db)
    bot = await repo.get_public(chatbot_id)
    if not bot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot not found")
    service = ChatService(db, bot["workspace_id"])
    return await service.escalate(conversation_id)


@public_router.post("/feedback")
async def submit_feedback(data: FeedbackRequest):
    from app.repositories.message_repository import MessageRepository
    db = get_database()
    msg_repo = MessageRepository(db)
    msg = await msg_repo.get_by_id(data.message_id)
    if not msg:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    service = FeedbackService(db, msg.get("workspace_id", ""))
    return await service.submit_feedback(data.message_id, data.rating, data.comment, data.thumbs)


@router.get("/conversations")
async def list_conversations(
    status: str | None = None,
    skip: int = 0,
    limit: int = 50,
    tenant: TenantContext = Depends(require_permission(Permission.LIVE_CHAT)),
):
    from app.services.conversation_service import ConversationService
    service = ConversationService(get_database(), tenant.workspace_id)
    items, total = await service.list_conversations(status, skip, limit)
    return {"items": items, "total": total}


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    tenant: TenantContext = Depends(require_permission(Permission.LIVE_CHAT)),
):
    from app.services.conversation_service import ConversationService
    service = ConversationService(get_database(), tenant.workspace_id)
    return await service.get_conversation(conversation_id)


@router.post("/conversations/{conversation_id}/assign")
async def assign_agent(
    conversation_id: str,
    agent_id: str,
    tenant: TenantContext = Depends(require_permission(Permission.LIVE_CHAT)),
):
    from app.services.conversation_service import ConversationService
    service = ConversationService(get_database(), tenant.workspace_id)
    return await service.assign_agent(conversation_id, agent_id)
