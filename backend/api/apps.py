import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"
    verbose_name = "SupportAI API"

    def ready(self) -> None:
        import mongoengine
        from django.conf import settings
        from mongoengine.connection import ConnectionFailure, get_connection

        try:
            get_connection(alias="default")
            return
        except ConnectionFailure:
            pass

        mongoengine.connect(
            db=settings.MONGODB_DB_NAME,
            host=settings.MONGODB_URL,
            alias="default",
        )
        logger.info(
            "MongoDB connected: db=%s",
            settings.MONGODB_DB_NAME,
        )
