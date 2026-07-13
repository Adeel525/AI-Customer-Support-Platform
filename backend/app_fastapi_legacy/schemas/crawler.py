from pydantic import BaseModel, HttpUrl


class CrawlerJobCreate(BaseModel):
    url: HttpUrl
    schedule: str = "weekly"
    max_depth: int = 2


class CrawlerJobResponse(BaseModel):
    id: str
    url: str
    schedule: str
    status: str
    last_sync: str | None = None
    pages_crawled: int = 0
