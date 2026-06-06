from fastapi import APIRouter, Depends

from app.core.database import get_database
from app.core.deps import Tenant, require_permission
from app.core.tenant import TenantContext
from app.models.enums import Permission
from app.schemas.chatbot import ChatbotCreate, ChatbotUpdate
from app.services.chatbot_service import ChatbotService

router = APIRouter(prefix="/chatbots", tags=["Chatbots"])


def get_service(tenant: Tenant) -> ChatbotService:
    return ChatbotService(get_database(), tenant.workspace_id)


@router.post("")
async def create_chatbot(
    data: ChatbotCreate,
    tenant: TenantContext = Depends(require_permission(Permission.MANAGE_CHATBOTS)),
    service: ChatbotService = Depends(get_service),
):
    return await service.create(data.model_dump())


@router.get("")
async def list_chatbots(
    skip: int = 0,
    limit: int = 50,
    tenant: TenantContext = Depends(require_permission(Permission.MANAGE_CHATBOTS)),
    service: ChatbotService = Depends(get_service),
):
    items, total = await service.list(skip, limit)
    return {"items": items, "total": total}


@router.get("/{chatbot_id}")
async def get_chatbot(
    chatbot_id: str,
    tenant: TenantContext = Depends(require_permission(Permission.MANAGE_CHATBOTS)),
    service: ChatbotService = Depends(get_service),
):
    return await service.get(chatbot_id)


@router.patch("/{chatbot_id}")
async def update_chatbot(
    chatbot_id: str,
    data: ChatbotUpdate,
    tenant: TenantContext = Depends(require_permission(Permission.MANAGE_CHATBOTS)),
    service: ChatbotService = Depends(get_service),
):
    return await service.update(chatbot_id, data.model_dump(exclude_none=True))


@router.delete("/{chatbot_id}")
async def delete_chatbot(
    chatbot_id: str,
    tenant: TenantContext = Depends(require_permission(Permission.MANAGE_CHATBOTS)),
    service: ChatbotService = Depends(get_service),
):
    await service.delete(chatbot_id)
    return {"message": "Chatbot deleted"}
