from fastapi import APIRouter, Depends

from app.core.database import get_database
from app.core.deps import Tenant, require_permission
from app.core.tenant import TenantContext
from app.models.enums import Permission
from app.services.analytics_service import AnalyticsService
from app.services.feedback_service import FeedbackService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def get_service(tenant: Tenant) -> AnalyticsService:
    return AnalyticsService(get_database(), tenant.workspace_id)


@router.get("/overview")
async def get_overview(
    tenant: TenantContext = Depends(require_permission(Permission.VIEW_ANALYTICS)),
    service: AnalyticsService = Depends(get_service),
):
    return await service.get_overview()


@router.get("/historical")
async def get_historical(
    start_date: str,
    end_date: str,
    tenant: TenantContext = Depends(require_permission(Permission.VIEW_ANALYTICS)),
    service: AnalyticsService = Depends(get_service),
):
    return await service.get_historical(start_date, end_date)


@router.get("/csat")
async def get_csat(tenant: TenantContext = Depends(require_permission(Permission.VIEW_ANALYTICS))):
    service = FeedbackService(get_database(), tenant.workspace_id)
    return await service.get_csat()
