export type JobAssetRead = {
  id: number;
  asset_type: string;
  object_key: string;
  original_name: string;
  content_type?: string | null;
  size_bytes: number;
};

export type JobRead = {
  id: string;
  prompt: string;
  target_language: string;
  status: string;
  progress: number;
  current_stage: string;
  runtime_minutes: number;
  final_video_key?: string | null;
  preview_page_key?: string | null;
  script_manifest_key?: string | null;
  job_manifest_key?: string | null;
  error_message?: string | null;
  assets: JobAssetRead[];
};

export type JobCreateResponse = {
  job: JobRead;
  socket_room: string;
  socket_namespace: string;
};

export type JobUpdate = {
  jobId: string;
  status: string;
  progress: number;
  stage: string;
  message: string;
  detail?: string;
};

export type ArtifactUrls = {
  preview_page_url?: string | null;
  final_video_url?: string | null;
  script_manifest_url?: string | null;
  job_manifest_url?: string | null;
};

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function parseResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with status ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export async function createJob(formData: FormData): Promise<JobCreateResponse> {
  const response = await fetch(`${apiBase}/api/jobs`, {
    method: "POST",
    body: formData
  });
  return parseResponse<JobCreateResponse>(response);
}

export async function getJob(jobId: string): Promise<JobRead> {
  const response = await fetch(`${apiBase}/api/jobs/${jobId}`, { cache: "no-store" });
  return parseResponse<JobRead>(response);
}

export async function getJobArtifacts(jobId: string): Promise<ArtifactUrls> {
  const response = await fetch(`${apiBase}/api/jobs/${jobId}/artifacts`, { cache: "no-store" });
  return parseResponse<ArtifactUrls>(response);
}
