from fastapi import HTTPException, status

from app.models.enums import SubscriptionPlan
from app.repositories.subscription_repository import SubscriptionRepository


class BillingService:
    """Stub service for Stripe billing integration."""

    PLAN_LIMITS = {
        SubscriptionPlan.FREE: {"documents": 10, "messages": 1000, "users": 2, "storage_mb": 100},
        SubscriptionPlan.STARTER: {"documents": 100, "messages": 10000, "users": 5, "storage_mb": 1000},
        SubscriptionPlan.PROFESSIONAL: {"documents": 1000, "messages": 100000, "users": 20, "storage_mb": 10000},
        SubscriptionPlan.ENTERPRISE: {"documents": -1, "messages": -1, "users": -1, "storage_mb": -1},
    }

    def __init__(self, db, workspace_id: str):
        self.workspace_id = workspace_id
        self.repo = SubscriptionRepository(db, workspace_id)

    async def get_subscription(self) -> dict:
        items, _ = await self.repo.list(limit=1)
        if items:
            return items[0]
        return {
            "workspace_id": self.workspace_id,
            "plan": SubscriptionPlan.FREE.value,
            "usage": {"documents": 0, "messages": 0, "users": 0},
        }

    async def create_checkout_session(self, plan: str) -> dict:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Stripe checkout not configured. Set STRIPE_SECRET_KEY.",
        )

    async def handle_webhook(self, payload: bytes, signature: str) -> dict:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Stripe webhook handler not configured.",
        )

    def get_plan_limits(self, plan: str) -> dict:
        return self.PLAN_LIMITS.get(SubscriptionPlan(plan), self.PLAN_LIMITS[SubscriptionPlan.FREE])
