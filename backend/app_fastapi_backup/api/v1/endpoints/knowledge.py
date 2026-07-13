from fastapi import APIRouter, Depends, File, UploadFile

from app.core.database import get_database
from app.core.deps import Tenant, require_permission
from app.core.tenant import TenantContext
from app.models.enums import Permission
from app.services.knowledge_service import KnowledgeService

router = APIRouter(prefix="/knowledge", tags=["Knowledge Base"])


def get_service(tenant: Tenant) -> KnowledgeService:
    return KnowledgeService(get_database(), tenant.workspace_id)


@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    tenant: TenantContext = Depends(require_permission(Permission.MANAGE_KNOWLEDGE)),
    service: KnowledgeService = Depends(get_service),
):
    return await service.upload_document(file)


@router.get("/documents")
async def list_documents(
    skip: int = 0,
    limit: int = 50,
    tenant: TenantContext = Depends(require_permission(Permission.MANAGE_KNOWLEDGE)),
    service: KnowledgeService = Depends(get_service),
):
    items, total = await service.list_documents(skip, limit)
    return {"items": items, "total": total, "page": skip // limit + 1, "page_size": limit}


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    tenant: TenantContext = Depends(require_permission(Permission.MANAGE_KNOWLEDGE)),
    service: KnowledgeService = Depends(get_service),
):
    await service.delete_document(document_id)
    return {"message": "Document deleted"}


@router.get("/stats")
async def get_knowledge_stats(
    tenant: TenantContext = Depends(require_permission(Permission.MANAGE_KNOWLEDGE)),
    service: KnowledgeService = Depends(get_service),
):
    return await service.get_stats()
