import JobForm from "@/components/job-form";

export default function HomePage() {
  return (
    <main className="page-shell">
      <section className="hero-card">
        <div className="eyebrow">Phase 1 to Phase 5 scaffold</div>
        <h1>AI Video Factory</h1>
        <p className="lede">
          FastAPI, Celery, Redis, PostgreSQL, MinIO, local-model orchestration, FFmpeg assembly,
          and a real-time Socket.IO progress UI for long-running 25-minute video jobs.
        </p>
        <JobForm />
      </section>
    </main>
  );
}
