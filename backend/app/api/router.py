from fastapi import APIRouter

from app.api.routes.health import router as health_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.metrics import router as metrics_router


api_router = APIRouter()
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(jobs_router, prefix="/jobs", tags=["jobs"])
api_router.include_router(metrics_router, prefix="/metrics", tags=["metrics"])
