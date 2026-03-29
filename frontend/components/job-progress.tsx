"use client";

import { useEffect, useMemo, useState } from "react";
import { io, Socket } from "socket.io-client";

import { getJob, getJobArtifacts, type ArtifactUrls, type JobRead, type JobUpdate } from "@/lib/api";

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const socketUrl = process.env.NEXT_PUBLIC_SOCKET_URL ?? apiBase;
const socketNamespace = process.env.NEXT_PUBLIC_SOCKET_NAMESPACE ?? "/ws";

export default function JobProgress({ jobId }: { jobId: string }) {
  const [job, setJob] = useState<JobRead | null>(null);
  const [artifacts, setArtifacts] = useState<ArtifactUrls | null>(null);
  const [events, setEvents] = useState<JobUpdate[]>([]);
  const [socketState, setSocketState] = useState("connecting");

  useEffect(() => {
    let active = true;
    let timer: ReturnType<typeof setInterval> | undefined;
    let socket: Socket | undefined;

    async function refreshJob() {
      const nextJob = await getJob(jobId);
      if (!active) {
        return;
      }
      setJob(nextJob);
      if (nextJob.status === "completed") {
        const nextArtifacts = await getJobArtifacts(jobId);
        if (active) {
          setArtifacts(nextArtifacts);
        }
      }
    }

    refreshJob().catch(() => undefined);
    timer = setInterval(() => {
      refreshJob().catch(() => undefined);
    }, 5000);

    socket = io(`${socketUrl}${socketNamespace}`, {
      path: "/socket.io",
      transports: ["websocket", "polling"]
    });

    socket.on("connect", () => {
      setSocketState("connected");
      socket?.emit("job:subscribe", { jobId });
    });

    socket.on("disconnect", () => {
      setSocketState("disconnected");
    });

    socket.on("job:update", (payload: JobUpdate) => {
      if (payload.jobId !== jobId) {
        return;
      }
      setEvents((current) => [payload, ...current].slice(0, 12));
      setJob((current) =>
        current
          ? {
              ...current,
              status: payload.status,
              progress: payload.progress,
              current_stage: payload.stage,
              error_message: payload.detail || current.error_message
            }
          : current
      );
      if (payload.status === "completed") {
        getJobArtifacts(jobId).then(setArtifacts).catch(() => undefined);
      }
    });

    return () => {
      active = false;
      if (timer) {
        clearInterval(timer);
      }
      socket?.disconnect();
    };
  }, [jobId]);

  const progressValue = useMemo(() => Math.max(0, Math.min(100, job?.progress ?? 0)), [job?.progress]);

  return (
    <div className="progress-stack">
      <div className="status-panel">
        <div className="status-row">
          <span>Socket</span>
          <strong>{socketState}</strong>
        </div>
        <div className="status-row">
          <span>Status</span>
          <strong>{job?.status ?? "loading"}</strong>
        </div>
        <div className="status-row">
          <span>Stage</span>
          <strong>{job?.current_stage ?? "starting"}</strong>
        </div>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${progressValue}%` }} />
        </div>
        <p>{Math.round(progressValue)}% complete</p>
        {job?.error_message ? <p className="error-text">{job.error_message}</p> : null}
      </div>

      <div className="status-panel">
        <h2>Latest events</h2>
        <ul className="event-list">
          {events.length === 0 ? <li>Waiting for worker events...</li> : null}
          {events.map((event, index) => (
            <li key={`${event.stage}-${index}`}>
              <strong>{event.stage}</strong>
              <span>{event.message}</span>
            </li>
          ))}
        </ul>
      </div>

      <div className="status-panel">
        <h2>Artifacts</h2>
        <ul className="artifact-list">
          <li>
            Preview page:{" "}
            {artifacts?.preview_page_url ? (
              <a href={artifacts.preview_page_url} target="_blank">
                Open preview
              </a>
            ) : (
              "pending"
            )}
          </li>
          <li>
            Script manifest:{" "}
            {artifacts?.script_manifest_url ? (
              <a href={artifacts.script_manifest_url} target="_blank">
                Open script manifest
              </a>
            ) : (
              "pending"
            )}
          </li>
          <li>
            Job manifest:{" "}
            {artifacts?.job_manifest_url ? (
              <a href={artifacts.job_manifest_url} target="_blank">
                Open assembly manifest
              </a>
            ) : (
              "pending"
            )}
          </li>
        </ul>
      </div>
    </div>
  );
}
