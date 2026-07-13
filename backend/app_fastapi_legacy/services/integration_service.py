from fastapi import HTTPException, status

from app.repositories.integration_repository import IntegrationRepository


class IntegrationService:
    """Stub service for WhatsApp, Slack, Email integrations."""

    def __init__(self, db, workspace_id: str):
        self.workspace_id = workspace_id
        self.repo = IntegrationRepository(db, workspace_id)

    async def list_integrations(self) -> list:
        items, _ = await self.repo.list()
        return items

    async def connect(self, integration_type: str, config: dict) -> dict:
        return await self.repo.create({
            "type": integration_type,
            "config": config,
            "is_active": True,
        })

    async def disconnect(self, integration_id: str) -> bool:
        return await self.repo.delete(integration_id)

    async def handle_webhook(self, integration_type: str, payload: dict) -> dict:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"{integration_type} webhook handler not yet implemented",
        )
