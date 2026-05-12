from celery import Celery
from app.config import REDIS_URL

celery_app = Celery(
    "ensemble_ai",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.core.workers.tasks"]   # ← Це головне!
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Kiev",
    enable_utc=True,
)