from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AI Video Factory"
    api_prefix: str = "/api"
    debug: bool = True
    log_level: str = "INFO"
    cors_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://127.0.0.1:3000"]
    )

    postgres_dsn: str = "postgresql+psycopg://video_user:video_pass@postgres:5432/video_factory"
    redis_url: str = "redis://redis:6379/0"

    minio_endpoint: str = "minio:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "video-assets"
    minio_secure: bool = False

    artifact_root: Path = Path("/tmp/video-factory")
    ffmpeg_binary: str = "ffmpeg"
    ffprobe_binary: str = "ffprobe"

    default_runtime_minutes: int = 25
    min_scene_seconds: int = 10
    max_scene_seconds: int = 15

    socket_namespace: str = "/ws"
    socket_channel: str = "video_factory_socketio"

    enable_demo_assets: bool = True


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.artifact_root.mkdir(parents=True, exist_ok=True)
    return settings
