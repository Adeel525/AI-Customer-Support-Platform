from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.models.enums import CrawlerStatus
from app.repositories.crawler_repository import CrawlerRepository
from app.services.knowledge_service import KnowledgeService
from app.utils.crawler import WebsiteCrawler


class CrawlerService:
    def __init__(self, db, workspace_id: str):
        self.workspace_id = workspace_id
        self.repo = CrawlerRepository(db, workspace_id)
        self.knowledge_service = KnowledgeService(db, workspace_id)

    async def create_job(self, url: str, schedule: str = "weekly", max_depth: int = 2) -> dict:
        return await self.repo.create({
            "url": str(url),
            "schedule": schedule,
            "max_depth": max_depth,
            "status": CrawlerStatus.PENDING.value,
            "pages_crawled": 0,
        })

    async def list_jobs(self) -> tuple:
        return await self.repo.list(sort=[("created_at", -1)])

    async def execute_crawl(self, job_id: str) -> dict:
        job = await self.repo.get_by_id(job_id)
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crawler job not found")

        await self.repo.update(job_id, {"status": CrawlerStatus.RUNNING.value})

        try:
            crawler = WebsiteCrawler(max_depth=job.get("max_depth", 2))
            pages = await crawler.crawl(job["url"])

            for page in pages:
                await self.knowledge_service.ingest_text(
                    title=page["title"],
                    content=page["content"],
                    source=page["url"],
                )

            return await self.repo.update(job_id, {
                "status": CrawlerStatus.COMPLETED.value,
                "pages_crawled": len(pages),
                "last_sync": datetime.now(timezone.utc),
            })
        except Exception as e:
            await self.repo.update(job_id, {
                "status": CrawlerStatus.FAILED.value,
                "error": str(e),
            })
            raise

    async def trigger_sync(self, job_id: str) -> dict:
        from app.workers.crawler_tasks import crawl_website
        crawl_website.delay(job_id, self.workspace_id)
        return {"status": "queued", "job_id": job_id}
