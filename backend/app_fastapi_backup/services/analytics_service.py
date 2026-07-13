from datetime import datetime, timezone

from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.feedback_repository import FeedbackRepository
from app.repositories.ticket_repository import TicketRepository


class AnalyticsService:
    def __init__(self, db, workspace_id: str):
        self.workspace_id = workspace_id
        self.analytics_repo = AnalyticsRepository(db, workspace_id)
        self.conversation_repo = ConversationRepository(db, workspace_id)
        self.ticket_repo = TicketRepository(db, workspace_id)
        self.feedback_repo = FeedbackRepository(db)
        self.db = db

    async def get_overview(self) -> dict:
        convs, total_conv = await self.conversation_repo.list(limit=10000)
        resolved = sum(1 for c in convs if c.get("status") == "resolved")
        escalated = sum(1 for c in convs if c.get("status") == "escalated")
        tickets, ticket_count = await self.ticket_repo.list(limit=10000)
        csat = await self.feedback_repo.get_csat_stats(self.workspace_id)

        confidences = [c.get("last_confidence", 0) for c in convs if c.get("last_confidence")]
        avg_confidence = sum(confidences) / max(len(confidences), 1)

        response_times = [c.get("avg_response_time_ms", 0) for c in convs if c.get("avg_response_time_ms")]
        avg_response = sum(response_times) / max(len(response_times), 1)

        return {
            "total_conversations": total_conv,
            "resolved_conversations": resolved,
            "escalated_conversations": escalated,
            "avg_response_time_ms": round(avg_response, 1),
            "csat_score": csat.get("csat_score", 0),
            "ticket_volume": ticket_count,
            "chatbot_accuracy": round(avg_confidence * 100, 1),
            "top_questions": await self._get_top_questions(),
            "confidence_trend": await self._get_confidence_trend(),
        }

    async def aggregate_for_date(self, date: str) -> dict:
        overview = await self.get_overview()
        return await self.analytics_repo.create({
            "date": date,
            "metrics": overview,
        })

    async def get_historical(self, start_date: str, end_date: str) -> list:
        return await self.analytics_repo.get_by_date_range(start_date, end_date)

    async def _get_top_questions(self) -> list:
        pipeline = [
            {"$match": {"workspace_id": self.workspace_id, "role": "user"}},
            {"$group": {"_id": "$content", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10},
        ]
        results = await self.db.messages.aggregate(pipeline).to_list(10)
        return [{"question": r["_id"][:100], "count": r["count"]} for r in results]

    async def _get_confidence_trend(self) -> list:
        records = await self.analytics_repo.get_by_date_range("2020-01-01", "2099-12-31")
        return [
            {"date": r.get("date"), "accuracy": r.get("metrics", {}).get("chatbot_accuracy", 0)}
            for r in records[-30:]
        ]
