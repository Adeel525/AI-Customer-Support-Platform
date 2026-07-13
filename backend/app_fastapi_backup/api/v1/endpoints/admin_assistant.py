from fastapi import APIRouter, Depends

from app.core.database import get_database
from app.core.deps import Tenant, require_roles
from app.core.tenant import TenantContext
from app.models.enums import UserRole
from app.services.admin_assistant_service import AdminAssistantService

router = APIRouter(prefix="/admin-assistant", tags=["Admin Assistant"])


@router.post("/query")
async def admin_query(
    question: str,
    tenant: TenantContext = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN)),
):
    service = AdminAssistantService(get_database(), tenant.workspace_id)
    return await service.query(question)
