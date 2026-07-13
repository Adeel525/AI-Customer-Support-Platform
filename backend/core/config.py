import os
from functools import lru_cache
from typing import List


def _env(key: str, default: str = "") -> str:
    """Read from django.conf.settings if available, else os.environ."""
    try:
        from django.conf import settings as dj_settings

        if dj_settings.configured and hasattr(dj_settings, key):
            value = getattr(dj_settings, key)
            if value is not None:
                return value
    except Exception:
        pass
    return os.environ.get(key, default)


def _env_bool(key: str, default: bool = False) -> bool:
    value = _env(key, str(default))
    if isinstance(value, bool):
        return value
    return str(value).lower() in ("1", "true", "yes", "on")


def _env_int(key: str, default: int = 0) -> int:
    value = _env(key, str(default))
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _env_float(key: str, default: float = 0.0) -> float:
    value = _env(key, str(default))
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


class Settings:
    def __init__(self) -> None:
        self.APP_NAME: str = _env("APP_NAME", "SupportAI")
        self.APP_ENV: str = _env("APP_ENV", "development")
        self.DEBUG: bool = _env_bool("DEBUG", True)
        self.SECRET_KEY: str = _env("SECRET_KEY", "change-me-to-a-random-secret-key")
        self.API_V1_PREFIX: str = _env("API_V1_PREFIX", "/api/v1")

        self.MONGODB_URL: str = _env("MONGODB_URL", "mongodb://localhost:27017")
        self.MONGODB_DB_NAME: str = _env("MONGODB_DB_NAME", "support_ai")

        self.REDIS_URL: str = _env("REDIS_URL", "redis://localhost:6379/0")

        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = _env_int("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
        self.REFRESH_TOKEN_EXPIRE_DAYS: int = _env_int("REFRESH_TOKEN_EXPIRE_DAYS", 7)

        self.GOOGLE_CLIENT_ID: str = _env("GOOGLE_CLIENT_ID", "")
        self.GOOGLE_CLIENT_SECRET: str = _env("GOOGLE_CLIENT_SECRET", "")
        self.GOOGLE_REDIRECT_URI: str = _env(
            "GOOGLE_REDIRECT_URI",
            "http://localhost:8000/api/v1/auth/google/callback",
        )

        self.FRONTEND_URL: str = _env("FRONTEND_URL", "http://localhost:3000")
        self.CORS_ORIGINS: str = _env(
            "CORS_ORIGINS",
            "http://localhost:3000,http://localhost:80",
        )

        self.SMTP_HOST: str = _env("SMTP_HOST", "")
        self.SMTP_PORT: int = _env_int("SMTP_PORT", 587)
        self.SMTP_USER: str = _env("SMTP_USER", "")
        self.SMTP_PASSWORD: str = _env("SMTP_PASSWORD", "")
        self.SMTP_FROM: str = _env("SMTP_FROM", "noreply@supportai.com")

        self.AWS_ACCESS_KEY_ID: str = _env("AWS_ACCESS_KEY_ID", "")
        self.AWS_SECRET_ACCESS_KEY: str = _env("AWS_SECRET_ACCESS_KEY", "")
        self.AWS_S3_BUCKET: str = _env("AWS_S3_BUCKET", "support-ai-documents")
        self.AWS_S3_REGION: str = _env("AWS_S3_REGION", "us-east-1")
        self.USE_LOCAL_STORAGE: bool = _env_bool("USE_LOCAL_STORAGE", True)
        self.LOCAL_STORAGE_PATH: str = _env("LOCAL_STORAGE_PATH", "./uploads")

        self.PINECONE_API_KEY: str = _env("PINECONE_API_KEY", "")
        self.PINECONE_INDEX_NAME: str = _env("PINECONE_INDEX_NAME", "support-kb")
        self.PINECONE_ENVIRONMENT: str = _env("PINECONE_ENVIRONMENT", "us-east-1")

        self.OPENAI_API_KEY: str = _env("OPENAI_API_KEY", "")
        self.OPENAI_MODEL: str = _env("OPENAI_MODEL", "gpt-4o")
        self.OPENAI_EMBEDDING_MODEL: str = _env(
            "OPENAI_EMBEDDING_MODEL",
            "text-embedding-3-small",
        )

        self.ANTHROPIC_API_KEY: str = _env("ANTHROPIC_API_KEY", "")

        self.STRIPE_SECRET_KEY: str = _env("STRIPE_SECRET_KEY", "")
        self.STRIPE_WEBHOOK_SECRET: str = _env("STRIPE_WEBHOOK_SECRET", "")

        self.CELERY_BROKER_URL: str = _env("CELERY_BROKER_URL", "redis://localhost:6379/1")
        self.CELERY_RESULT_BACKEND: str = _env(
            "CELERY_RESULT_BACKEND",
            "redis://localhost:6379/2",
        )

        self.CHUNK_SIZE: int = _env_int("CHUNK_SIZE", 800)
        self.CHUNK_OVERLAP: int = _env_int("CHUNK_OVERLAP", 150)
        self.RAG_TOP_K: int = _env_int("RAG_TOP_K", 20)
        self.RAG_RERANK_TOP_K: int = _env_int("RAG_RERANK_TOP_K", 5)
        self.CONFIDENCE_THRESHOLD: float = _env_float("CONFIDENCE_THRESHOLD", 0.6)

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
