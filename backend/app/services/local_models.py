import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List


@dataclass
class ScenePlan:
    scene_id: int
    start_time_sec: int
    duration_sec: int
    visual_prompt: str
    narration_text: str
    continuity_hint: str


class LocalScriptPlanner:
    def generate(self, prompt: str, runtime_minutes: int, min_scene_sec: int, max_scene_sec: int) -> dict:
        total_seconds = runtime_minutes * 60
        average_scene = (min_scene_sec + max_scene_sec) // 2
        scene_count = max(1, total_seconds // average_scene)
        scenes: List[ScenePlan] = []
        cursor = 0
        for index in range(1, scene_count + 1):
            duration = min(max_scene_sec if index % 2 == 0 else min_scene_sec, total_seconds - cursor)
            if duration <= 0:
                break
            scenes.append(
                ScenePlan(
                    scene_id=index,
                    start_time_sec=cursor,
                    duration_sec=duration,
                    visual_prompt=f"{prompt} | scene {index} | cinematic composition | consistent wardrobe and lighting",
                    narration_text=f"Scene {index} advances the story of {prompt} with cinematic continuity.",
                    continuity_hint="Preserve hero design, palette, costume, camera language, and set dressing.",
                )
            )
            cursor += duration

        return {
            "title": prompt[:80],
            "runtime_minutes": runtime_minutes,
            "scene_count": len(scenes),
            "scenes": [asdict(scene) for scene in scenes],
        }


class LocalVideoModel:
    def render_scene(self, working_dir: Path, scene: dict) -> Path:
        scene_path = working_dir / f"scene-{scene['scene_id']:03d}.json"
        scene_path.write_text(json.dumps(scene, indent=2), encoding="utf-8")
        return scene_path


class LocalTTSModel:
    def synthesize(self, working_dir: Path, scene: dict, language: str) -> Path:
        tts_path = working_dir / f"scene-{scene['scene_id']:03d}-{language}.txt"
        tts_path.write_text(scene["narration_text"], encoding="utf-8")
        return tts_path


class LocalDubModel:
    def dub(self, narration: str, target_language: str) -> str:
        if target_language.lower() == "en":
            return narration
        return f"[{target_language}] {narration}"


class LocalLipSyncModel:
    def sync(self, working_dir: Path, scene: dict, audio_path: Path, video_path: Path) -> Path:
        output = working_dir / f"scene-{scene['scene_id']:03d}-lipsync.txt"
        output.write_text(
            f"Lip-sync placeholder for {video_path.name} with {audio_path.name}",
            encoding="utf-8",
        )
        return output
