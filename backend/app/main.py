import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import socketio

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.session import Base, engine
from app.socket import sio
from app.api.routes.metrics import REQUEST_COUNT, REQUEST_LATENCY


settings = get_settings()
configure_logging(settings.log_level)
fastapi_app = FastAPI(title=settings.app_name, debug=settings.debug)

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

fastapi_app.include_router(api_router, prefix=settings.api_prefix)


@fastapi_app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start
    path = request.url.path
    REQUEST_COUNT.labels(request.method, path, str(response.status_code)).inc()
    REQUEST_LATENCY.labels(request.method, path).observe(duration)
    return response


@fastapi_app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app, socketio_path="socket.io")
