from fastapi import APIRouter, Depends

from app.core.database import get_database
from app.core.deps import Tenant, require_permission
from app.core.tenant import TenantContext
from app.models.enums import Permission
from app.schemas.crawler import CrawlerJobCreate
from app.services.crawler_service import CrawlerService

router = APIRouter(prefix="/crawler", tags=["Website Crawler"])


def get_service(tenant: Tenant) -> CrawlerService:
    return CrawlerService(get_database(), tenant.workspace_id)


@router.post("/jobs")
async def create_crawler_job(
    data: CrawlerJobCreate,
    tenant: TenantContext = Depends(require_permission(Permission.MANAGE_KNOWLEDGE)),
    service: CrawlerService = Depends(get_service),
):
    job = await service.create_job(str(data.url), data.schedule, data.max_depth)
    result = await service.trigger_sync(job["id"])
    return {**job, **result}


@router.get("/jobs")
async def list_crawler_jobs(
    tenant: TenantContext = Depends(require_permission(Permission.MANAGE_KNOWLEDGE)),
    service: CrawlerService = Depends(get_service),
):
    items, total = await service.list_jobs()
    return {"items": items, "total": total}


@router.post("/jobs/{job_id}/sync")
async def trigger_sync(
    job_id: str,
    tenant: TenantContext = Depends(require_permission(Permission.MANAGE_KNOWLEDGE)),
    service: CrawlerService = Depends(get_service),
):
    return await service.trigger_sync(job_id)
