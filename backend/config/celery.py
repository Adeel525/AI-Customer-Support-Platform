import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("support_ai")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "aggregate-analytics-daily": {
        "task": "api.tasks.aggregate_daily_analytics",
        "schedule": crontab(hour=2, minute=0),
    },
    "sync-crawler-jobs": {
        "task": "api.tasks.sync_scheduled_crawlers",
        "schedule": crontab(hour=3, minute=0),
    },
}
app.conf.timezone = "UTC"
