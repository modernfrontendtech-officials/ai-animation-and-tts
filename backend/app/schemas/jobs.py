from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class JobAssetRead(BaseModel):
    id: int
    asset_type: str
    object_key: str
    original_name: str
    content_type: Optional[str] = None
    size_bytes: int

    model_config = {"from_attributes": True}


class JobRead(BaseModel):
    id: str
    prompt: str
    target_language: str
    status: str
    progress: float
    current_stage: str
    runtime_minutes: int
    final_video_key: Optional[str] = None
    preview_page_key: Optional[str] = None
    script_manifest_key: Optional[str] = None
    job_manifest_key: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    assets: List[JobAssetRead] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class JobCreateResponse(BaseModel):
    job: JobRead
    socket_room: str
    socket_namespace: str


class JobProgressEvent(BaseModel):
    job_id: str
    status: str
    progress: float
    stage: str
    message: str
    detail: Optional[str] = None


class JobArtifactUrls(BaseModel):
    preview_page_url: Optional[str] = None
    final_video_url: Optional[str] = None
    script_manifest_url: Optional[str] = None
    job_manifest_url: Optional[str] = None
