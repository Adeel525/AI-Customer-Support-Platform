"""
Mongoengine Document models matching FastAPI MongoDB collections.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from mongoengine import Document as MongoDocument
from mongoengine.fields import (
    BooleanField,
    DateTimeField,
    DictField,
    FloatField,
    IntField,
    ListField,
    ObjectIdField,
    StringField,
)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TimestampedDocument(MongoDocument):
    """Abstract base with created_at / updated_at timestamps."""

    meta = {"abstract": True}

    created_at = DateTimeField(default=_utcnow)
    updated_at = DateTimeField(default=_utcnow)

    def save(self, *args: Any, **kwargs: Any):
        self.updated_at = _utcnow()
        if not self.created_at:
            self.created_at = self.updated_at
        return super().save(*args, **kwargs)


def serialize_doc(doc: MongoDocument | None, exclude: set[str] | None = None) -> dict[str, Any] | None:
    """Convert a mongoengine document to a JSON-friendly dict."""
    if doc is None:
        return None

    exclude = exclude or set()
    data = doc.to_mongo().to_dict()
    raw_id = data.pop("_id", None)
    if raw_id is not None:
        data["id"] = str(raw_id)

    for key in list(data.keys()):
        if key in exclude:
            data.pop(key, None)
            continue
        value = data[key]
        if isinstance(value, datetime):
            data[key] = value.isoformat()
        elif hasattr(value, "__iter__") and not isinstance(value, (str, bytes, dict)):
            data[key] = [
                item.isoformat()
                if isinstance(item, datetime)
                else str(item)
                if type(item).__name__ == "ObjectId"
                else item
                for item in value
            ]
        elif type(value).__name__ == "ObjectId":
            data[key] = str(value)

    return data


# ---------------------------------------------------------------------------
# Users & workspaces
# ---------------------------------------------------------------------------


class User(TimestampedDocument):
    meta = {
        "collection": "users",
        "indexes": [
            {"fields": ["email"], "unique": True},
        ],
    }

    email = StringField(required=True, unique=True, max_length=255)
    password_hash = StringField()
    full_name = StringField(required=True, max_length=255)
    is_verified = BooleanField(default=False)
    oauth_provider = StringField(default=None, null=True)
    verification_token = StringField(default=None, null=True)
    reset_token = StringField(default=None, null=True)
    reset_token_expires = DateTimeField(default=None, null=True)
    avatar_url = StringField(default=None, null=True)

    def to_dict(self) -> dict[str, Any]:
        data = {
            "id": str(self.id),
            "email": self.email,
            "full_name": self.full_name,
            "is_verified": bool(self.is_verified),
            "oauth_provider": self.oauth_provider,
            "verification_token": self.verification_token,
            "reset_token": self.reset_token,
            "reset_token_expires": (
                self.reset_token_expires.isoformat() if self.reset_token_expires else None
            ),
            "avatar_url": self.avatar_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        return data


class Workspace(TimestampedDocument):
    meta = {
        "collection": "workspaces",
        "indexes": [
            {"fields": ["slug"], "unique": True},
        ],
    }

    name = StringField(required=True, max_length=255)
    slug = StringField(required=True, unique=True, max_length=255)
    branding = DictField(default=dict)
    settings = DictField(default=dict)
    plan = StringField(default="free", max_length=50)


class WorkspaceMember(TimestampedDocument):
    meta = {
        "collection": "workspace_members",
        "indexes": [
            {"fields": ["workspace_id", "user_id"], "unique": True},
        ],
    }

    workspace_id = StringField(required=True)
    user_id = StringField(required=True)
    role = StringField(required=True, max_length=50)


# ---------------------------------------------------------------------------
# Knowledge
# ---------------------------------------------------------------------------


class Document(TimestampedDocument):
    meta = {
        "collection": "documents",
        "indexes": ["workspace_id"],
    }

    workspace_id = StringField(required=True)
    filename = StringField(required=True)
    file_type = StringField(default="")
    s3_key = StringField(default="")
    status = StringField(default="pending")
    token_count = IntField(default=0)
    page_count = IntField(default=0)
    chunk_count = IntField(default=0)
    source = StringField(default="upload")
    file_size = IntField(default=0)
    error = StringField(default=None, null=True)


class DocumentChunk(TimestampedDocument):
    meta = {
        "collection": "document_chunks",
        "indexes": [
            ("workspace_id", "document_id"),
        ],
    }

    workspace_id = StringField(required=True)
    document_id = StringField(required=True)
    chunk_id = StringField(required=True)
    content = StringField(required=True)
    page_number = IntField(default=1)
    source = StringField(default="")
    token_count = IntField(default=0)
    embedding_model = StringField(default="text-embedding-3-small")


# ---------------------------------------------------------------------------
# Chatbots & conversations
# ---------------------------------------------------------------------------


class Chatbot(TimestampedDocument):
    meta = {
        "collection": "chatbots",
        "indexes": ["workspace_id"],
    }

    workspace_id = StringField(required=True)
    name = StringField(required=True, max_length=255)
    welcome_message = StringField(default="Hi! How can I help you today?")
    primary_color = StringField(default="#10b981")
    theme = StringField(default="light")
    language = StringField(default="en")
    tone = StringField(default="professional")
    personality = StringField(default="support")
    avatar_url = StringField(default=None, null=True)
    document_ids = ListField(StringField(), default=list)
    is_active = BooleanField(default=True)


class Conversation(TimestampedDocument):
    meta = {
        "collection": "conversations",
        "indexes": [
            ("workspace_id", "status"),
        ],
    }

    workspace_id = StringField(required=True)
    chatbot_id = StringField(required=True)
    customer_id = StringField(default=None, null=True)
    status = StringField(default="active")
    message_count = IntField(default=0)
    last_message_at = DateTimeField(default=None, null=True)
    last_confidence = FloatField(default=None, null=True)
    assigned_agent_id = StringField(default=None, null=True)
    summary = StringField(default=None, null=True)
    summarized_at = DateTimeField(default=None, null=True)


class Message(TimestampedDocument):
    meta = {
        "collection": "messages",
        "indexes": ["conversation_id"],
    }

    conversation_id = StringField(required=True)
    workspace_id = StringField(required=True)
    role = StringField(required=True)
    content = StringField(required=True)
    confidence = FloatField(default=None, null=True)
    sources = ListField(DictField(), default=list)
    author_id = StringField(default=None, null=True)


# ---------------------------------------------------------------------------
# Tickets & feedback
# ---------------------------------------------------------------------------


class Ticket(TimestampedDocument):
    meta = {
        "collection": "tickets",
        "indexes": [
            ("workspace_id", "status"),
        ],
    }

    workspace_id = StringField(required=True)
    title = StringField(required=True)
    description = StringField(default="")
    category = StringField(default="technical")
    priority = StringField(default="medium")
    status = StringField(default="open")
    conversation_id = StringField(default=None, null=True)
    created_by = StringField(default=None, null=True)
    assigned_agent_id = StringField(default=None, null=True)
    ai_summary = StringField(default=None, null=True)
    detected_intent = StringField(default=None, null=True)
    suggested_resolution = StringField(default=None, null=True)
    confidence_at_escalation = FloatField(default=None, null=True)
    auto_generated = BooleanField(default=False)


class TicketComment(TimestampedDocument):
    meta = {
        "collection": "ticket_comments",
        "indexes": ["ticket_id"],
    }

    ticket_id = StringField(required=True)
    workspace_id = StringField(required=True)
    author_id = StringField(required=True)
    content = StringField(required=True)
    is_internal = BooleanField(default=False)


class Feedback(TimestampedDocument):
    meta = {
        "collection": "feedback",
        "indexes": ["message_id"],
    }

    workspace_id = StringField(required=True)
    message_id = StringField(required=True)
    rating = IntField(default=None, null=True, min_value=1, max_value=5)
    comment = StringField(default=None, null=True)
    thumbs = StringField(default=None, null=True)


# ---------------------------------------------------------------------------
# Billing, API keys, crawler, integrations
# ---------------------------------------------------------------------------


class Analytics(TimestampedDocument):
    meta = {
        "collection": "analytics",
        "indexes": [
            {"fields": ["workspace_id", "date"], "unique": True},
        ],
    }

    workspace_id = StringField(required=True)
    date = StringField(required=True)  # YYYY-MM-DD
    metrics = DictField(default=dict)


class Subscription(TimestampedDocument):
    meta = {
        "collection": "subscriptions",
        "indexes": [
            {"fields": ["workspace_id"], "unique": True},
        ],
    }

    workspace_id = StringField(required=True, unique=True)
    plan = StringField(default="free")
    stripe_customer_id = StringField(default=None, null=True)
    usage = DictField(default=lambda: {"documents": 0, "messages": 0, "users": 0})


class ApiKey(TimestampedDocument):
    meta = {
        "collection": "api_keys",
        "indexes": [
            {"fields": ["key_hash"], "unique": True},
            "workspace_id",
        ],
    }

    workspace_id = StringField(required=True)
    name = StringField(required=True)
    key_hash = StringField(required=True, unique=True)
    key_prefix = StringField(required=True)
    permissions = ListField(StringField(), default=lambda: ["read"])
    rate_limit = IntField(default=1000)
    is_active = BooleanField(default=True)


class CrawlerJob(TimestampedDocument):
    meta = {
        "collection": "crawler_jobs",
        "indexes": ["workspace_id"],
    }

    workspace_id = StringField(required=True)
    url = StringField(required=True)
    schedule = StringField(default="weekly")
    max_depth = IntField(default=2)
    status = StringField(default="pending")
    pages_crawled = IntField(default=0)
    last_sync = DateTimeField(default=None, null=True)
    error = StringField(default=None, null=True)


class Integration(TimestampedDocument):
    meta = {
        "collection": "integrations",
        "indexes": [
            ("workspace_id", "type"),
        ],
    }

    workspace_id = StringField(required=True)
    type = StringField(required=True)
    config = DictField(default=dict)
    is_active = BooleanField(default=True)


# ---------------------------------------------------------------------------
# Audit & notifications
# ---------------------------------------------------------------------------


class AuditLog(TimestampedDocument):
    meta = {
        "collection": "audit_logs",
        "indexes": [
            ("workspace_id", "-timestamp"),
        ],
    }

    workspace_id = StringField(required=True)
    user_id = StringField(required=True)
    action = StringField(required=True)
    resource = StringField(default="")
    method = StringField(default="")
    status_code = IntField(default=200)
    duration_ms = FloatField(default=0.0)
    timestamp = DateTimeField(default=_utcnow)


class Notification(TimestampedDocument):
    meta = {
        "collection": "notifications",
        "indexes": ["user_id"],
    }

    user_id = StringField(required=True)
    type = StringField(required=True)
    content = StringField(required=True)
    is_read = BooleanField(default=False)


# Re-export ObjectIdField so callers can use api.models.ObjectIdField
__all__ = [
    "ObjectIdField",
    "serialize_doc",
    "TimestampedDocument",
    "User",
    "Workspace",
    "WorkspaceMember",
    "Document",
    "DocumentChunk",
    "Chatbot",
    "Conversation",
    "Message",
    "Ticket",
    "TicketComment",
    "Feedback",
    "Analytics",
    "Subscription",
    "ApiKey",
    "CrawlerJob",
    "Integration",
    "AuditLog",
    "Notification",
]
