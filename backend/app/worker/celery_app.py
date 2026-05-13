from celery import Celery
from app.config import settings

celery = Celery(
    "scorify",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery.conf.update(
    task_track_started=True,
    result_expires=86400,  # 24 hours
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
)
