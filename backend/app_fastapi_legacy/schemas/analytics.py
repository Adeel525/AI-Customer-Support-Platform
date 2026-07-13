from pydantic import BaseModel


class AnalyticsOverview(BaseModel):
    total_conversations: int = 0
    resolved_conversations: int = 0
    escalated_conversations: int = 0
    avg_response_time_ms: float = 0
    csat_score: float = 0
    ticket_volume: int = 0
    chatbot_accuracy: float = 0
    top_questions: list[dict] = []
    confidence_trend: list[dict] = []
