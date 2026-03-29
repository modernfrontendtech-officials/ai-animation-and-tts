from celery import Celery

from app.core.config import get_settings


settings = get_settings()

celery_app = Celery(
    "video_factory",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.task_routes = {"app.tasks.pipeline.run_video_job": {"queue": "gpu-jobs"}}
