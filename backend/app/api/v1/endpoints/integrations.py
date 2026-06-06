from fastapi import APIRouter, Depends

from app.core.database import get_database
from app.core.deps import Tenant, require_permission
from app.core.tenant import TenantContext
from app.models.enums import Permission
from app.services.integration_service import IntegrationService

router = APIRouter(prefix="/integrations", tags=["Integrations"])


def get_service(tenant: Tenant) -> IntegrationService:
    return IntegrationService(get_database(), tenant.workspace_id)


@router.get("")
async def list_integrations(
    tenant: TenantContext = Depends(require_permission(Permission.MANAGE_INTEGRATIONS)),
    service: IntegrationService = Depends(get_service),
):
    return await service.list_integrations()


@router.post("/{integration_type}/connect")
async def connect_integration(
    integration_type: str,
    config: dict,
    tenant: TenantContext = Depends(require_permission(Permission.MANAGE_INTEGRATIONS)),
    service: IntegrationService = Depends(get_service),
):
    return await service.connect(integration_type, config)


@router.delete("/{integration_id}")
async def disconnect_integration(
    integration_id: str,
    tenant: TenantContext = Depends(require_permission(Permission.MANAGE_INTEGRATIONS)),
    service: IntegrationService = Depends(get_service),
):
    await service.disconnect(integration_id)
    return {"message": "Integration disconnected"}


@router.post("/webhooks/whatsapp")
async def whatsapp_webhook(payload: dict, service: IntegrationService = Depends(get_service)):
    return await service.handle_webhook("whatsapp", payload)


@router.post("/webhooks/slack")
async def slack_webhook(payload: dict, service: IntegrationService = Depends(get_service)):
    return await service.handle_webhook("slack", payload)
