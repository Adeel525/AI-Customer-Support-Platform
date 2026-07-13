from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    status: str
    token_count: int = 0
    page_count: int = 0
    source: str = "upload"
    created_at: str | None = None


class KnowledgeBaseStats(BaseModel):
    total_documents: int = 0
    pages_indexed: int = 0
    tokens_indexed: int = 0
    last_sync_time: str | None = None
    coverage_score: float = 0.0
