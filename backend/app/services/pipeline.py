import json
from pathlib import Path

from app.core.config import get_settings
from app.services.assembly import AssemblyService
from app.services.local_models import LocalDubModel, LocalLipSyncModel, LocalScriptPlanner, LocalTTSModel, LocalVideoModel
from app.services.storage import StorageService


class LocalPipelineService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.storage = StorageService()
        self.script_planner = LocalScriptPlanner()
        self.video_model = LocalVideoModel()
        self.tts_model = LocalTTSModel()
        self.dub_model = LocalDubModel()
        self.lip_sync_model = LocalLipSyncModel()
        self.assembly = AssemblyService()

    def prepare_working_dir(self, job_id: str) -> Path:
        working_dir = self.settings.artifact_root / job_id
        working_dir.mkdir(parents=True, exist_ok=True)
        return working_dir

    def build_script_package(self, job_id: str, prompt: str, runtime_minutes: int) -> tuple[Path, dict]:
        working_dir = self.prepare_working_dir(job_id)
        script = self.script_planner.generate(
            prompt,
            runtime_minutes,
            self.settings.min_scene_seconds,
            self.settings.max_scene_seconds,
        )
        manifest_path = working_dir / "script_package.json"
        manifest_path.write_text(json.dumps(script, indent=2), encoding="utf-8")
        return manifest_path, script

    def render_scene_bundle(self, job_id: str, scene: dict, target_language: str) -> dict:
        working_dir = self.prepare_working_dir(job_id)
        dubbed_text = self.dub_model.dub(scene["narration_text"], target_language)
        scene_for_render = dict(scene)
        scene_for_render["narration_text"] = dubbed_text
        video_path = self.video_model.render_scene(working_dir, scene_for_render)
        audio_path = self.tts_model.synthesize(working_dir, scene_for_render, target_language)
        lipsync_path = self.lip_sync_model.sync(working_dir, scene_for_render, audio_path, video_path)
        return {
            "scene_id": scene["scene_id"],
            "video_path": video_path,
            "audio_path": audio_path,
            "lipsync_path": lipsync_path,
        }

    def upload_artifact(self, local_path: Path, object_key: str, content_type: str) -> str:
        self.storage.upload_file(object_key, local_path, content_type=content_type)
        return object_key

    def finalize(self, job_id: str, prompt: str, scene_count: int) -> dict:
        working_dir = self.prepare_working_dir(job_id)
        ffmpeg_script = self.assembly.build_ffmpeg_script(working_dir, scene_count)
        preview_page = self.assembly.build_preview_html(working_dir, job_id, prompt)
        final_manifest = working_dir / "job_manifest.json"
        final_manifest.write_text(
            json.dumps(
                {
                    "job_id": job_id,
                    "scene_count": scene_count,
                    "preview_page": preview_page.name,
                    "ffmpeg_script": ffmpeg_script.name,
                    "next_step": "Connect real model outputs and invoke ffmpeg/moviepy assembly.",
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        return {
            "preview_page": preview_page,
            "ffmpeg_script": ffmpeg_script,
            "final_manifest": final_manifest,
        }
