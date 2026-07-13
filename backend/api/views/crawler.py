"""
Website crawler API views.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.authentication import JWTAuthentication, get_workspace_id
from api.models import CrawlerJob, serialize_doc
from api.permissions import HasWorkspacePermission, IsAuthenticatedJWT
from api.serializers import CrawlerJobCreateSerializer
from api.services.knowledge import ingest_text
from core.enums import CrawlerStatus, Permission
from core.utils.crawler import WebsiteCrawler

logger = logging.getLogger(__name__)


def _execute_crawl(job_id: str, workspace_id: str) -> dict:
    job = CrawlerJob.objects(id=job_id, workspace_id=workspace_id).first()
    if not job:
        raise ValueError("Crawler job not found")

    job.status = CrawlerStatus.RUNNING.value
    job.error = None
    job.save()

    try:
        crawler = WebsiteCrawler(max_depth=job.max_depth or 2)
        pages = crawler.crawl(job.url)

        for page in pages:
            try:
                ingest_text(
                    workspace_id,
                    title=page.get("title") or "Untitled",
                    content=page.get("content") or "",
                    source=page.get("url") or job.url,
                )
            except Exception:
                logger.exception("Failed to ingest crawled page %s", page.get("url"))

        job.status = CrawlerStatus.COMPLETED.value
        job.pages_crawled = len(pages)
        job.last_sync = datetime.now(timezone.utc)
        job.error = None
        job.save()
        return serialize_doc(job)
    except Exception as exc:
        job.status = CrawlerStatus.FAILED.value
        job.error = str(exc)
        job.save()
        raise


def _queue_or_crawl(job_id: str, workspace_id: str) -> dict:
    try:
        from api.tasks import crawl_website

        crawl_website.delay(job_id, workspace_id)
        return {"status": "queued", "job_id": job_id}
    except Exception:
        pass

    try:
        result = _execute_crawl(job_id, workspace_id)
        return {"status": "completed", "job_id": job_id, **(result or {})}
    except Exception as exc:
        logger.exception("Crawl failed for job %s", job_id)
        return {"status": "failed", "job_id": job_id, "error": str(exc)}


class CrawlerJobListCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedJWT, HasWorkspacePermission(Permission.MANAGE_KNOWLEDGE.value)]

    def get(self, request):
        ws_id = get_workspace_id(request)
        qs = CrawlerJob.objects(workspace_id=ws_id).order_by("-created_at")
        items = [serialize_doc(j) for j in qs]
        return Response({"items": items, "total": len(items)})

    def post(self, request):
        ws_id = get_workspace_id(request)
        ser = CrawlerJobCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        job = CrawlerJob(
            workspace_id=ws_id,
            url=str(data["url"]),
            schedule=data.get("schedule", "weekly"),
            max_depth=data.get("max_depth", 2),
            status=CrawlerStatus.PENDING.value,
            pages_crawled=0,
        )
        job.save()
        sync_result = _queue_or_crawl(str(job.id), ws_id)
        job.reload()
        return Response({**(serialize_doc(job) or {}), **sync_result}, status=status.HTTP_201_CREATED)


class CrawlerJobSyncView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedJWT, HasWorkspacePermission(Permission.MANAGE_KNOWLEDGE.value)]

    def post(self, request, job_id):
        ws_id = get_workspace_id(request)
        job = CrawlerJob.objects(id=job_id, workspace_id=ws_id).first()
        if not job:
            return Response({"detail": "Crawler job not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(_queue_or_crawl(job_id, ws_id))
