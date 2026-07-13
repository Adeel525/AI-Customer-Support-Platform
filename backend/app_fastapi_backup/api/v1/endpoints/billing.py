from fastapi import APIRouter, Depends, Request

from app.core.database import get_database
from app.core.deps import Tenant, require_permission
from app.core.tenant import TenantContext
from app.models.enums import Permission
from app.services.billing_service import BillingService

router = APIRouter(prefix="/billing", tags=["Billing"])


def get_service(tenant: Tenant) -> BillingService:
    return BillingService(get_database(), tenant.workspace_id)


@router.get("/subscription")
async def get_subscription(
    tenant: TenantContext = Depends(require_permission(Permission.MANAGE_BILLING)),
    service: BillingService = Depends(get_service),
):
    return await service.get_subscription()


@router.post("/checkout")
async def create_checkout(
    plan: str,
    tenant: TenantContext = Depends(require_permission(Permission.MANAGE_BILLING)),
    service: BillingService = Depends(get_service),
):
    return await service.create_checkout_session(plan)


@router.post("/webhook")
async def stripe_webhook(request: Request):
    from app.core.database import get_database
    from app.services.billing_service import BillingService
    body = await request.body()
    signature = request.headers.get("stripe-signature", "")
    service = BillingService(get_database(), "")
    return await service.handle_webhook(body, signature)
