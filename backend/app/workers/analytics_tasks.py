import asyncio
import logging
from datetime import datetime, timedelta, timezone

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task
def aggregate_daily_analytics():
    from app.core.database import connect_to_mongo, get_database
    from app.services.analytics_service import AnalyticsService

    async def _aggregate():
        await connect_to_mongo()
        db = get_database()
        yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
        cursor = db.workspaces.find({})
        workspaces = await cursor.to_list(1000)
        for ws in workspaces:
            ws_id = str(ws["_id"])
            service = AnalyticsService(db, ws_id)
            await service.aggregate_for_date(yesterday)

    _run_async(_aggregate())


@celery_app.task
def summarize_conversation(conversation_id: str, workspace_id: str):
    from app.core.database import connect_to_mongo, get_database
    from app.services.conversation_service import ConversationService

    async def _summarize():
        await connect_to_mongo()
        db = get_database()
        service = ConversationService(db, workspace_id)
        await service.summarize_conversation(conversation_id)

    _run_async(_summarize())
