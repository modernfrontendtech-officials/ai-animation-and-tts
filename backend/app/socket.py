import socketio

from app.core.config import get_settings


settings = get_settings()

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=settings.cors_origins,
    client_manager=socketio.AsyncRedisManager(settings.redis_url, channel=settings.socket_channel),
)


@sio.event(namespace=settings.socket_namespace)
async def connect(sid, environ, auth):
    return True


@sio.event(namespace=settings.socket_namespace)
async def disconnect(sid):
    return None


@sio.on("job:subscribe", namespace=settings.socket_namespace)
async def job_subscribe(sid, payload):
    job_id = payload["jobId"]
    await sio.enter_room(sid, f"job:{job_id}", namespace=settings.socket_namespace)
    await sio.emit(
        "job:subscribed",
        {"jobId": job_id, "room": f"job:{job_id}"},
        room=sid,
        namespace=settings.socket_namespace,
    )
