from fastapi import APIRouter, Depends

from app.core.database import get_database
from app.core.deps import Tenant, require_permission
from app.core.tenant import TenantContext
from app.models.enums import Permission
from app.services.api_platform_service import ApiPlatformService

router = APIRouter(prefix="/api-keys", tags=["API Platform"])


def get_service(tenant: Tenant) -> ApiPlatformService:
    return ApiPlatformService(get_database(), tenant.workspace_id)


@router.post("")
async def create_api_key(
    name: str,
    tenant: TenantContext = Depends(require_permission(Permission.MANAGE_WORKSPACE)),
    service: ApiPlatformService = Depends(get_service),
):
    return await service.create_api_key(name)


@router.get("")
async def list_api_keys(
    tenant: TenantContext = Depends(require_permission(Permission.MANAGE_WORKSPACE)),
    service: ApiPlatformService = Depends(get_service),
):
    return await service.list_api_keys()


@router.delete("/{key_id}")
async def revoke_api_key(
    key_id: str,
    tenant: TenantContext = Depends(require_permission(Permission.MANAGE_WORKSPACE)),
    service: ApiPlatformService = Depends(get_service),
):
    await service.revoke_api_key(key_id)
    return {"message": "API key revoked"}
