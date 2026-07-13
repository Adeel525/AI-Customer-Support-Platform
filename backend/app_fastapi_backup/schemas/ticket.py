from pydantic import BaseModel, Field


class TicketCreate(BaseModel):
    title: str = Field(min_length=1)
    description: str
    category: str = "technical"
    priority: str = "medium"
    conversation_id: str | None = None


class TicketUpdate(BaseModel):
    title: str | None = None
    status: str | None = None
    priority: str | None = None
    assigned_agent_id: str | None = None
    category: str | None = None


class TicketCommentCreate(BaseModel):
    content: str = Field(min_length=1)
    is_internal: bool = False


class TicketResponse(BaseModel):
    id: str
    title: str
    description: str
    category: str
    priority: str
    status: str
    conversation_id: str | None = None
    assigned_agent_id: str | None = None
    ai_summary: str | None = None
    detected_intent: str | None = None
    suggested_resolution: str | None = None
