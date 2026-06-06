from pydantic import BaseModel, Field


class ChatbotCreate(BaseModel):
    name: str = Field(min_length=1)
    welcome_message: str = "Hi! How can I help you today?"
    primary_color: str = "#10b981"
    theme: str = "light"
    language: str = "en"
    tone: str = "professional"
    personality: str = "support"
    avatar_url: str | None = None
    document_ids: list[str] = []


class ChatbotUpdate(BaseModel):
    name: str | None = None
    welcome_message: str | None = None
    primary_color: str | None = None
    theme: str | None = None
    language: str | None = None
    tone: str | None = None
    personality: str | None = None
    avatar_url: str | None = None
    is_active: bool | None = None
    document_ids: list[str] | None = None


class ChatbotResponse(BaseModel):
    id: str
    name: str
    welcome_message: str
    primary_color: str
    theme: str
    language: str
    tone: str
    personality: str
    is_active: bool
    avatar_url: str | None = None
