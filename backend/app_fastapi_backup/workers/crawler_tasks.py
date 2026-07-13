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


@celery_app.task(bind=True, max_retries=2)
def crawl_website(self, job_id: str, workspace_id: str):
    from app.services.crawler_service import CrawlerService
    from app.core.database import connect_to_mongo, get_database

    async def _crawl():
        await connect_to_mongo()
        db = get_database()
        service = CrawlerService(db, workspace_id)
        await service.execute_crawl(job_id)

    try:
        _run_async(_crawl())
    except Exception as exc:
        logger.error("Crawl failed: %s", exc)
        raise self.retry(exc=exc, countdown=120)


@celery_app.task
def sync_scheduled_crawlers():
    from app.services.crawler_service import CrawlerService
    from app.core.database import connect_to_mongo, get_database

    async def _sync():
        await connect_to_mongo()
        db = get_database()
        cursor = db.crawler_jobs.find({"status": {"$ne": "running"}})
        jobs = await cursor.to_list(100)
        for job in jobs:
            service = CrawlerService(db, job["workspace_id"])
            await service.execute_crawl(str(job["_id"]))

    _run_async(_sync())
