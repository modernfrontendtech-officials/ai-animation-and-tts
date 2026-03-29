from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from app.db.session import engine
from app.services.storage import StorageService


router = APIRouter()


@router.get("/live")
def live() -> dict:
    return {"status": "ok"}


@router.get("/ready")
def ready() -> dict:
    checks: dict[str, str] = {}

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        checks["postgres"] = "ok"
    except Exception as exc:  # noqa: BLE001
        checks["postgres"] = f"error: {exc}"

    try:
        storage = StorageService()
        storage.ensure_bucket()
        checks["minio"] = "ok"
    except Exception as exc:  # noqa: BLE001
        checks["minio"] = f"error: {exc}"

    try:
        from app.services.progress import manager

        manager._redis.connect().ping()
        checks["redis"] = "ok"
    except Exception as exc:  # noqa: BLE001
        checks["redis"] = f"error: {exc}"

    failed = [name for name, value in checks.items() if value != "ok"]
    if failed:
        raise HTTPException(status_code=503, detail={"status": "degraded", "checks": checks})

    return {"status": "ok", "checks": checks}
