from fastapi import APIRouter, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest


router = APIRouter()

REQUEST_COUNT = Counter(
    "ai_video_factory_http_requests_total",
    "Total HTTP requests handled by the backend.",
    ["method", "path", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "ai_video_factory_http_request_duration_seconds",
    "HTTP request latency in seconds.",
    ["method", "path"],
)


@router.get("")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
