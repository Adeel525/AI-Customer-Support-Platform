from fastapi import APIRouter, Depends

from app.core.database import get_database
from app.core.deps import Tenant, require_permission
from app.core.tenant import TenantContext
from app.models.enums import Permission
from app.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["Semantic Search"])


@router.get("")
async def semantic_search(
    q: str,
    entity_types: str | None = None,
    tenant: TenantContext = Depends(require_permission(Permission.MANAGE_KNOWLEDGE)),
):
    types = entity_types.split(",") if entity_types else None
    service = SearchService(get_database(), tenant.workspace_id)
    return await service.semantic_search(q, types)
