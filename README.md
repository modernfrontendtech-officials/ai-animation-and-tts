# AI Video Factory

Self-hosted scaffold for a long-form AI video generation platform with:

- FastAPI backend
- Celery + Redis job queue
- PostgreSQL metadata
- MinIO object storage
- Local model service interfaces for script, video, TTS, dubbing, and lip-sync
- FFmpeg/MoviePy assembly seam
- Static HTML/CSS/JavaScript frontend with live Socket.IO progress updates

## Structure

- `backend/`: API, worker, storage, queue, and local-model orchestration
- `frontend/`: plain HTML frontend served by Nginx
- `docker-compose.yml`: local dev stack for Postgres, Redis, MinIO, backend, worker, and frontend

## Run locally

1. Copy `.env.example` to `.env` if you want to customize values.
2. Start the stack:

```bash
docker compose up --build
```

3. Open:

- Frontend: `http://localhost:3000`
- Backend docs: `http://localhost:8000/docs`
- MinIO console: `http://localhost:9001`

## Current model status

The code is intentionally scaffolded around self-hosted model interfaces. The queue, storage, progress, upload, and assembly flow are real. The heavy GPU stages currently use placeholder local services, so the next engineering step is swapping these classes with your production runners for:

- Stable Video Diffusion or CogVideoX
- XTTS v2 or Bark
- SeamlessM4T
- Wav2Lip or SadTalker

## Backend flow

1. User creates a job from the frontend.
2. FastAPI stores metadata in PostgreSQL and uploads media to MinIO.
3. Celery pushes the long-running render into Redis-backed workers.
4. Worker emits progress events through Redis-backed Socket.IO rooms.
5. Frontend listens live and updates the progress page.

## Notes

- `backend/app/services/local_models.py` is the main integration seam for your self-hosted models.
- `backend/app/services/assembly.py` is where FFmpeg command generation lives.
- `backend/app/tasks/pipeline.py` is the orchestration path to extend for chunked GPU rendering and retries.
- `frontend/index.html` and `frontend/job.html` are now the active frontend pages.
- `frontend/config.js` is where the browser-side API and socket endpoints are configured.
