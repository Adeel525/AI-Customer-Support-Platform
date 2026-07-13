from fastapi import APIRouter, Depends

from app.core.database import get_database
from app.core.deps import CurrentUser, Tenant, require_permission
from app.core.tenant import TenantContext
from app.models.enums import Permission
from app.schemas.workspace import BrandingUpdate, MemberInvite, MemberRoleUpdate, WorkspaceUpdate
from app.services.workspace_service import WorkspaceService

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


def get_service(tenant: Tenant) -> WorkspaceService:
    return WorkspaceService(get_database(), tenant.workspace_id)


@router.get("/current")
async def get_current_workspace(tenant: Tenant, service: WorkspaceService = Depends(get_service)):
    return await service.get_workspace()


@router.patch("/current")
async def update_workspace(
    data: WorkspaceUpdate,
    tenant: TenantContext = Depends(require_permission(Permission.MANAGE_WORKSPACE)),
    service: WorkspaceService = Depends(get_service),
):
    return await service.update_workspace(data.model_dump(exclude_none=True))


@router.patch("/current/branding")
async def update_branding(
    data: BrandingUpdate,
    tenant: TenantContext = Depends(require_permission(Permission.MANAGE_WORKSPACE)),
    service: WorkspaceService = Depends(get_service),
):
    return await service.update_branding(data.model_dump(exclude_none=True))


@router.get("/current/members")
async def list_members(tenant: Tenant, service: WorkspaceService = Depends(get_service)):
    return await service.list_members()


@router.post("/current/members")
async def invite_member(
    data: MemberInvite,
    user: CurrentUser,
    tenant: TenantContext = Depends(require_permission(Permission.MANAGE_MEMBERS)),
    service: WorkspaceService = Depends(get_service),
):
    return await service.invite_member(data.email, data.role, user.get("full_name", "Admin"))


@router.patch("/current/members/{user_id}")
async def update_member_role(
    user_id: str,
    data: MemberRoleUpdate,
    tenant: TenantContext = Depends(require_permission(Permission.MANAGE_MEMBERS)),
    service: WorkspaceService = Depends(get_service),
):
    return await service.update_member_role(user_id, data.role)


@router.delete("/current/members/{user_id}")
async def remove_member(
    user_id: str,
    tenant: TenantContext = Depends(require_permission(Permission.MANAGE_MEMBERS)),
    service: WorkspaceService = Depends(get_service),
):
    await service.remove_member(user_id)
    return {"message": "Member removed"}
