from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.database import get_database
from app.core.security import decode_token
from app.core.tenant import TenantContext
from app.models.enums import ROLE_PERMISSIONS, Permission, UserRole
from app.repositories.user_repository import UserRepository
from app.repositories.workspace_member_repository import WorkspaceMemberRepository

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
):
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    payload = decode_token(credentials.credentials)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    db = get_database()
    user = await UserRepository(db).get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


async def get_current_active_user(user=Depends(get_current_user)):
    if not user.get("is_verified", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email not verified")
    return user


async def get_tenant_context(
    request: Request,
    user=Depends(get_current_active_user),
    x_workspace_id: Annotated[str | None, Header(alias="X-Workspace-Id")] = None,
) -> TenantContext:
    workspace_id = x_workspace_id
    role = None

    credentials = request.headers.get("authorization", "")
    if credentials.startswith("Bearer "):
        payload = decode_token(credentials[7:])
        if payload:
            workspace_id = workspace_id or payload.get("workspace_id")
            role = payload.get("role")

    if not workspace_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workspace ID required (X-Workspace-Id header or token claim)",
        )

    db = get_database()
    member = await WorkspaceMemberRepository(db).get_member(workspace_id, user["id"])
    if not member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a workspace member")

    tenant = TenantContext(
        workspace_id=workspace_id,
        user_id=user["id"],
        role=member["role"],
    )
    request.state.tenant = tenant
    return tenant


def require_permission(permission: Permission):
    async def checker(tenant: TenantContext = Depends(get_tenant_context)):
        role = UserRole(tenant.role)
        allowed = ROLE_PERMISSIONS.get(role, set())
        if permission not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission.value}",
            )
        return tenant

    return checker


def require_roles(*roles: UserRole):
    async def checker(tenant: TenantContext = Depends(get_tenant_context)):
        if UserRole(tenant.role) not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return tenant

    return checker


CurrentUser = Annotated[dict, Depends(get_current_active_user)]
Tenant = Annotated[TenantContext, Depends(get_tenant_context)]
