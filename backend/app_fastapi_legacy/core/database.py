from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings

_client: AsyncIOMotorClient | None = None


async def connect_to_mongo() -> None:
    global _client
    _client = AsyncIOMotorClient(settings.MONGODB_URL)


async def close_mongo_connection() -> None:
    global _client
    if _client:
        _client.close()
        _client = None


def get_database() -> AsyncIOMotorDatabase:
    if _client is None:
        raise RuntimeError("MongoDB client not initialized")
    return _client[settings.MONGODB_DB_NAME]


async def create_indexes() -> None:
    db = get_database()

    await db.users.create_index("email", unique=True)
    await db.workspaces.create_index("slug", unique=True)
    await db.workspace_members.create_index([("workspace_id", 1), ("user_id", 1)], unique=True)
    await db.documents.create_index("workspace_id")
    await db.document_chunks.create_index([("workspace_id", 1), ("document_id", 1)])
    await db.chatbots.create_index("workspace_id")
    await db.conversations.create_index([("workspace_id", 1), ("status", 1)])
    await db.messages.create_index("conversation_id")
    await db.tickets.create_index([("workspace_id", 1), ("status", 1)])
    await db.ticket_comments.create_index("ticket_id")
    await db.feedback.create_index("message_id")
    await db.analytics.create_index([("workspace_id", 1), ("date", 1)], unique=True)
    await db.subscriptions.create_index("workspace_id", unique=True)
    await db.api_keys.create_index("key_hash", unique=True)
    await db.audit_logs.create_index([("workspace_id", 1), ("timestamp", -1)])
    await db.notifications.create_index("user_id")
    await db.crawler_jobs.create_index("workspace_id")
    await db.integrations.create_index([("workspace_id", 1), ("type", 1)])
