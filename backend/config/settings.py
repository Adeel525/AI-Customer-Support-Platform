"""
Django settings for SupportAI backend.

Primary data store is MongoDB via mongoengine.
SQLite is used only for Django admin / sessions / auth tables.
"""
from pathlib import Path

import environ

from core.settings_helpers import csv_list, env_bool

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------
SECRET_KEY = env("SECRET_KEY", default="change-me-to-a-random-secret-key")
DEBUG = env_bool(env("DEBUG", default="True"))
APP_NAME = env("APP_NAME", default="SupportAI")
APP_ENV = env("APP_ENV", default="development")
ALLOWED_HOSTS = csv_list(env("ALLOWED_HOSTS", default="localhost,127.0.0.1,*"))
APPEND_SLASH = False

# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "corsheaders",
    "channels",
    # Local
    "api.apps.ApiConfig",
    "core.apps.CoreConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ---------------------------------------------------------------------------
# Database (dummy SQLite for Django admin / sessions; app data is MongoDB)
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ---------------------------------------------------------------------------
# MongoDB (mongoengine — connected in api.apps.ApiConfig.ready())
# ---------------------------------------------------------------------------
MONGODB_URL = env("MONGODB_URL", default="mongodb://localhost:27017")
MONGODB_DB_NAME = env("MONGODB_DB_NAME", default="support_ai")

# ---------------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
FRONTEND_URL = env("FRONTEND_URL", default="http://localhost:3000")
CORS_ALLOWED_ORIGINS = csv_list(
    env("CORS_ORIGINS", default="http://localhost:3000,http://localhost:80")
)
CORS_ALLOW_CREDENTIALS = True

# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------
# API auth uses custom JWT for mongoengine users (not Django's User model).
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "api.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.FormParser",
    ],
    "EXCEPTION_HANDLER": "rest_framework.views.exception_handler",
    "UNAUTHENTICATED_USER": None,
}

# ---------------------------------------------------------------------------
# JWT (custom — for mongoengine users; PyJWT)
# ---------------------------------------------------------------------------
ACCESS_TOKEN_EXPIRE_MINUTES = env.int("ACCESS_TOKEN_EXPIRE_MINUTES", default=30)
REFRESH_TOKEN_EXPIRE_DAYS = env.int("REFRESH_TOKEN_EXPIRE_DAYS", default=7)
API_V1_PREFIX = env("API_V1_PREFIX", default="/api/v1")

# ---------------------------------------------------------------------------
# Redis / Celery
# ---------------------------------------------------------------------------
REDIS_URL = env("REDIS_URL", default="redis://localhost:6379/0")
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://localhost:6379/1")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://localhost:6379/2")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"
CELERY_ENABLE_UTC = True

# ---------------------------------------------------------------------------
# Channels (optional WebSockets — in-memory for local/dev without Redis)
# ---------------------------------------------------------------------------
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

# ---------------------------------------------------------------------------
# OAuth / Google
# ---------------------------------------------------------------------------
GOOGLE_CLIENT_ID = env("GOOGLE_CLIENT_ID", default="")
GOOGLE_CLIENT_SECRET = env("GOOGLE_CLIENT_SECRET", default="")
GOOGLE_REDIRECT_URI = env(
    "GOOGLE_REDIRECT_URI",
    default="http://localhost:8000/api/v1/auth/google/callback",
)

# ---------------------------------------------------------------------------
# Email / SMTP
# ---------------------------------------------------------------------------
SMTP_HOST = env("SMTP_HOST", default="")
SMTP_PORT = env.int("SMTP_PORT", default=587)
SMTP_USER = env("SMTP_USER", default="")
SMTP_PASSWORD = env("SMTP_PASSWORD", default="")
SMTP_FROM = env("SMTP_FROM", default="noreply@supportai.com")

# ---------------------------------------------------------------------------
# Storage (S3 / local)
# ---------------------------------------------------------------------------
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID", default="")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY", default="")
AWS_S3_BUCKET = env("AWS_S3_BUCKET", default="support-ai-documents")
AWS_S3_REGION = env("AWS_S3_REGION", default="us-east-1")
USE_LOCAL_STORAGE = env_bool(env("USE_LOCAL_STORAGE", default="True"))
LOCAL_STORAGE_PATH = env("LOCAL_STORAGE_PATH", default=str(BASE_DIR / "uploads"))

# ---------------------------------------------------------------------------
# AI / RAG providers
# ---------------------------------------------------------------------------
PINECONE_API_KEY = env("PINECONE_API_KEY", default="")
PINECONE_INDEX_NAME = env("PINECONE_INDEX_NAME", default="support-kb")
PINECONE_ENVIRONMENT = env("PINECONE_ENVIRONMENT", default="us-east-1")

OPENAI_API_KEY = env("OPENAI_API_KEY", default="")
OPENAI_MODEL = env("OPENAI_MODEL", default="gpt-4o")
OPENAI_EMBEDDING_MODEL = env("OPENAI_EMBEDDING_MODEL", default="text-embedding-3-small")

ANTHROPIC_API_KEY = env("ANTHROPIC_API_KEY", default="")

CHUNK_SIZE = env.int("CHUNK_SIZE", default=800)
CHUNK_OVERLAP = env.int("CHUNK_OVERLAP", default=150)
RAG_TOP_K = env.int("RAG_TOP_K", default=20)
RAG_RERANK_TOP_K = env.int("RAG_RERANK_TOP_K", default=5)
CONFIDENCE_THRESHOLD = env.float("CONFIDENCE_THRESHOLD", default=0.6)

# ---------------------------------------------------------------------------
# Stripe
# ---------------------------------------------------------------------------
STRIPE_SECRET_KEY = env("STRIPE_SECRET_KEY", default="")
STRIPE_WEBHOOK_SECRET = env("STRIPE_WEBHOOK_SECRET", default="")

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "api": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "pymongo": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}
