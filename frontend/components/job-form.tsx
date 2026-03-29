"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { createJob } from "@/lib/api";

export default function JobForm() {
  const router = useRouter();
  const [prompt, setPrompt] = useState("");
  const [targetLanguage, setTargetLanguage] = useState("en");
  const [runtimeMinutes, setRuntimeMinutes] = useState(25);
  const [files, setFiles] = useState<FileList | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append("prompt", prompt);
      formData.append("target_language", targetLanguage);
      formData.append("runtime_minutes", String(runtimeMinutes));
      Array.from(files ?? []).forEach((file) => formData.append("files", file));

      const response = await createJob(formData);
      router.push(`/jobs/${response.job.id}`);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Failed to create job.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="job-form" onSubmit={handleSubmit}>
      <label>
        Story prompt
        <textarea
          value={prompt}
          onChange={(event) => setPrompt(event.target.value)}
          placeholder="Describe the 25-minute story, style, tone, and character continuity."
          required
          rows={6}
        />
      </label>

      <div className="grid-two">
        <label>
          Target language
          <select value={targetLanguage} onChange={(event) => setTargetLanguage(event.target.value)}>
            <option value="en">English</option>
            <option value="hi">Hindi</option>
            <option value="ta">Tamil</option>
            <option value="te">Telugu</option>
          </select>
        </label>

        <label>
          Runtime in minutes
          <input
            type="number"
            min={1}
            max={60}
            value={runtimeMinutes}
            onChange={(event) => setRuntimeMinutes(Number(event.target.value))}
          />
        </label>
      </div>

      <label>
        Reference video or audio uploads
        <input type="file" multiple onChange={(event) => setFiles(event.target.files)} />
      </label>

      <button className="primary-button" type="submit" disabled={submitting}>
        {submitting ? "Queueing job..." : "Start Render Job"}
      </button>

      {error ? <p className="error-text">{error}</p> : null}
    </form>
  );
}
