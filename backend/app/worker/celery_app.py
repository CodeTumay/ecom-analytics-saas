from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "jewelpilot",
    broker=settings.broker_url,
    backend=settings.result_backend,
    include=["app.worker.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)
