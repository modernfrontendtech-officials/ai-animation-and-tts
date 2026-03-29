# Kubernetes Starters

These manifests are intentionally lightweight starters for Phase 4.

- `backend-deployment.yaml`: API pods behind a ClusterIP service
- `worker-gpu-deployment.yaml`: GPU-targeted Celery workers
- `frontend-deployment.yaml`: Next.js UI deployment and service

Before applying them, you will still need:

1. A Kubernetes cluster with NVIDIA device plugin installed.
2. `ai-video-secrets` and `frontend-config` resources.
3. Managed or in-cluster PostgreSQL, Redis, and S3-compatible object storage.
