from pydantic import BaseModel, Field


class ChatMessageRequest(BaseModel):
    message: str = Field(min_length=1)
    conversation_id: str | None = None
    customer_id: str | None = None


class ChatMessageResponse(BaseModel):
    conversation_id: str
    message_id: str
    content: str
    confidence: float = 0.0
    sources: list[dict] = []
    should_escalate: bool = False


class FeedbackRequest(BaseModel):
    message_id: str
    rating: int = Field(ge=1, le=5)
    comment: str | None = None
    thumbs: str | None = None  # "up" or "down"
