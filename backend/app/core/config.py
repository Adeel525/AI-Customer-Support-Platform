from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "SupportAI"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me-to-a-random-secret-key"
    API_V1_PREFIX: str = "/api/v1"

    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "support_ai"

    REDIS_URL: str = "redis://localhost:6379/0"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"

    FRONTEND_URL: str = "http://localhost:3000"
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:80"

    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@supportai.com"

    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_S3_BUCKET: str = "support-ai-documents"
    AWS_S3_REGION: str = "us-east-1"
    USE_LOCAL_STORAGE: bool = True
    LOCAL_STORAGE_PATH: str = "./uploads"

    PINECONE_API_KEY: str = ""
    PINECONE_INDEX_NAME: str = "support-kb"
    PINECONE_ENVIRONMENT: str = "us-east-1"

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    ANTHROPIC_API_KEY: str = ""

    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 150
    RAG_TOP_K: int = 20
    RAG_RERANK_TOP_K: int = 5
    CONFIDENCE_THRESHOLD: float = 0.6

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
