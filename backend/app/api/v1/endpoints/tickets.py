from fastapi import APIRouter, Depends

from app.core.database import get_database
from app.core.deps import CurrentUser, Tenant, require_permission
from app.core.tenant import TenantContext
from app.models.enums import Permission
from app.schemas.ticket import TicketCommentCreate, TicketCreate, TicketUpdate
from app.services.ticket_service import TicketService

router = APIRouter(prefix="/tickets", tags=["Tickets"])


def get_service(tenant: Tenant) -> TicketService:
    return TicketService(get_database(), tenant.workspace_id)


@router.post("")
async def create_ticket(
    data: TicketCreate,
    user: CurrentUser,
    tenant: TenantContext = Depends(require_permission(Permission.MANAGE_TICKETS)),
    service: TicketService = Depends(get_service),
):
    return await service.create(data.model_dump(), user["id"])


@router.get("")
async def list_tickets(
    status: str | None = None,
    skip: int = 0,
    limit: int = 50,
    tenant: TenantContext = Depends(require_permission(Permission.MANAGE_TICKETS)),
    service: TicketService = Depends(get_service),
):
    items, total = await service.list(status, skip, limit)
    return {"items": items, "total": total}


@router.get("/{ticket_id}")
async def get_ticket(
    ticket_id: str,
    tenant: TenantContext = Depends(require_permission(Permission.MANAGE_TICKETS)),
    service: TicketService = Depends(get_service),
):
    return await service.get(ticket_id)


@router.patch("/{ticket_id}")
async def update_ticket(
    ticket_id: str,
    data: TicketUpdate,
    tenant: TenantContext = Depends(require_permission(Permission.MANAGE_TICKETS)),
    service: TicketService = Depends(get_service),
):
    return await service.update(ticket_id, data.model_dump(exclude_none=True))


@router.post("/{ticket_id}/comments")
async def add_comment(
    ticket_id: str,
    data: TicketCommentCreate,
    user: CurrentUser,
    tenant: TenantContext = Depends(require_permission(Permission.MANAGE_TICKETS)),
    service: TicketService = Depends(get_service),
):
    return await service.add_comment(ticket_id, data.content, user["id"], data.is_internal)


@router.get("/{ticket_id}/comments")
async def list_comments(
    ticket_id: str,
    tenant: TenantContext = Depends(require_permission(Permission.MANAGE_TICKETS)),
    service: TicketService = Depends(get_service),
):
    return await service.list_comments(ticket_id)
