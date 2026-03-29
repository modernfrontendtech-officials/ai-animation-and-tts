from sqlalchemy.orm import Session

from app.celery_app import celery_app
from app.db.models import Job
from app.db.session import SessionLocal
from app.services.pipeline import LocalPipelineService
from app.services.progress import emit_job_progress


def _set_job_state(
    db: Session,
    job: Job,
    *,
    status: str,
    progress: float,
    stage: str,
    message: str,
    error_message: str | None = None,
) -> None:
    job.status = status
    job.progress = progress
    job.current_stage = stage
    job.error_message = error_message
    db.add(job)
    db.commit()
    db.refresh(job)
    emit_job_progress(job.id, status, progress, stage, message, error_message or "")


@celery_app.task(name="app.tasks.pipeline.run_video_job")
def run_video_job(job_id: str) -> None:
    db = SessionLocal()
    pipeline = LocalPipelineService()
    try:
        job = db.get(Job, job_id)
        if job is None:
            return

        _set_job_state(
            db,
            job,
            status="running",
            progress=5,
            stage="script-planning",
            message="Generating long-form script and scene partitioning.",
        )
        script_path, script_payload = pipeline.build_script_package(job.id, job.prompt, job.runtime_minutes)
        job.script_manifest_key = pipeline.upload_artifact(
            script_path,
            f"jobs/{job.id}/script_package.json",
            "application/json",
        )
        db.add(job)
        db.commit()

        total_scenes = max(1, len(script_payload["scenes"]))
        for index, scene in enumerate(script_payload["scenes"], start=1):
            progress = 10 + (index / total_scenes) * 70
            _set_job_state(
                db,
                job,
                status="running",
                progress=progress,
                stage="scene-render",
                message=f"Rendering scene {index} of {total_scenes}.",
            )
            pipeline.render_scene_bundle(job.id, scene, job.target_language)

        _set_job_state(
            db,
            job,
            status="running",
            progress=90,
            stage="assembly",
            message="Preparing FFmpeg assembly and preview artifacts.",
        )
        artifacts = pipeline.finalize(job.id, job.prompt, total_scenes)
        job.preview_page_key = pipeline.upload_artifact(
            artifacts["preview_page"],
            f"jobs/{job.id}/preview.html",
            "text/html",
        )
        job.job_manifest_key = pipeline.upload_artifact(
            artifacts["final_manifest"],
            f"jobs/{job.id}/job_manifest.json",
            "application/json",
        )
        db.add(job)
        db.commit()

        _set_job_state(
            db,
            job,
            status="completed",
            progress=100,
            stage="completed",
            message="Job completed. Preview and manifest are ready.",
        )
    except Exception as exc:  # noqa: BLE001
        job = db.get(Job, job_id)
        if job is not None:
            _set_job_state(
                db,
                job,
                status="failed",
                progress=job.progress,
                stage="failed",
                message="Job failed during processing.",
                error_message=str(exc),
            )
        raise
    finally:
        db.close()
