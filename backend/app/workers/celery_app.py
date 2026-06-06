from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "support_ai",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "aggregate-analytics-daily": {
            "task": "app.workers.analytics_tasks.aggregate_daily_analytics",
            "schedule": crontab(hour=2, minute=0),
        },
        "sync-crawler-jobs": {
            "task": "app.workers.crawler_tasks.sync_scheduled_crawlers",
            "schedule": crontab(hour=3, minute=0),
        },
    },
)

celery_app.autodiscover_tasks(["app.workers"])
