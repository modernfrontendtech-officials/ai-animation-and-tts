import socketio

from app.core.config import get_settings


settings = get_settings()
manager = socketio.RedisManager(settings.redis_url, channel=settings.socket_channel, write_only=True)


def emit_job_progress(job_id: str, status: str, progress: float, stage: str, message: str, detail: str = "") -> None:
    manager.emit(
        "job:update",
        {
            "jobId": job_id,
            "status": status,
            "progress": progress,
            "stage": stage,
            "message": message,
            "detail": detail,
        },
        room=f"job:{job_id}",
        namespace=settings.socket_namespace,
    )
