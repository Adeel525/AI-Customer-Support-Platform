from fastapi import HTTPException, status

from app.ai.llm_client import LLMClient
from app.services.analytics_service import AnalyticsService


class AdminAssistantService:
    """AI assistant for admin analytics queries."""

    def __init__(self, db, workspace_id: str):
        self.workspace_id = workspace_id
        self.analytics = AnalyticsService(db, workspace_id)
        self.llm = LLMClient()

    async def query(self, question: str) -> dict:
        overview = await self.analytics.get_overview()
        context = f"Analytics data: {overview}"
        response = await self.llm.generate([
            {"role": "system", "content": "You are an admin analytics assistant. Answer based on the provided data."},
            {"role": "user", "content": f"Data:\n{context}\n\nQuestion: {question}"},
        ])
        return {"answer": response, "data": overview}
