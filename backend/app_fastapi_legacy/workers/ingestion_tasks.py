import asyncio
import logging

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(bind=True, max_retries=3)
def process_document(self, document_id: str, workspace_id: str):
    from app.services.knowledge_service import KnowledgeService
    from app.core.database import connect_to_mongo, get_database

    async def _process():
        await connect_to_mongo()
        db = get_database()
        service = KnowledgeService(db, workspace_id)
        await service.process_document(document_id)

    try:
        _run_async(_process())
    except Exception as exc:
        logger.error("Document processing failed: %s", exc)
        raise self.retry(exc=exc, countdown=60)
