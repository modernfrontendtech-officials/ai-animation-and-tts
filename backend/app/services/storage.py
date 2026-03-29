from io import BytesIO
from pathlib import Path

from minio import Minio
from minio.error import S3Error

from app.core.config import get_settings


class StorageService:
    def __init__(self) -> None:
        settings = get_settings()
        self.bucket = settings.minio_bucket
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )

    def ensure_bucket(self) -> None:
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def upload_bytes(self, object_key: str, payload: bytes, content_type: str) -> None:
        self.ensure_bucket()
        self.client.put_object(
            self.bucket,
            object_key,
            BytesIO(payload),
            length=len(payload),
            content_type=content_type,
        )

    def upload_file(self, object_key: str, file_path: Path, content_type: str = "application/octet-stream") -> None:
        self.ensure_bucket()
        self.client.fput_object(self.bucket, object_key, str(file_path), content_type=content_type)

    def presigned_url(self, object_key: str) -> str:
        self.ensure_bucket()
        return self.client.presigned_get_object(self.bucket, object_key)
