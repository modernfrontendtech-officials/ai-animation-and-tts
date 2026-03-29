from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import Job, JobAsset
from app.db.session import get_db
from app.schemas.jobs import JobArtifactUrls, JobCreateResponse, JobRead
from app.services.storage import StorageService
from app.tasks.pipeline import run_video_job


router = APIRouter()
settings = get_settings()


@router.post("", response_model=JobCreateResponse)
async def create_job(
    prompt: Annotated[str, Form(...)],
    target_language: Annotated[str, Form("en")],
    runtime_minutes: Annotated[int, Form(settings.default_runtime_minutes)],
    files: Annotated[list[UploadFile] | None, File()] = None,
    db: Session = Depends(get_db),
):
    storage = StorageService()
    job = Job(
        prompt=prompt,
        target_language=target_language,
        runtime_minutes=runtime_minutes,
        status="queued",
        progress=0,
        current_stage="queued",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    for upload in files or []:
        payload = await upload.read()
        object_key = f"jobs/{job.id}/inputs/{upload.filename}"
        storage.upload_bytes(object_key, payload, upload.content_type or "application/octet-stream")
        db.add(
            JobAsset(
                job_id=job.id,
                asset_type="upload",
                object_key=object_key,
                original_name=upload.filename or "upload.bin",
                content_type=upload.content_type,
                size_bytes=len(payload),
            )
        )

    db.commit()
    db.refresh(job)
    run_video_job.delay(job.id)
    return JobCreateResponse(
        job=JobRead.model_validate(job),
        socket_room=f"job:{job.id}",
        socket_namespace=settings.socket_namespace,
    )


@router.get("/{job_id}", response_model=JobRead)
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobRead.model_validate(job)


@router.get("/{job_id}/artifacts", response_model=JobArtifactUrls)
def get_job_artifacts(job_id: str, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    storage = StorageService()
    return JobArtifactUrls(
        preview_page_url=storage.presigned_url(job.preview_page_key) if job.preview_page_key else None,
        final_video_url=storage.presigned_url(job.final_video_key) if job.final_video_key else None,
        script_manifest_url=storage.presigned_url(job.script_manifest_key) if job.script_manifest_key else None,
        job_manifest_url=storage.presigned_url(job.job_manifest_key) if job.job_manifest_key else None,
    )
