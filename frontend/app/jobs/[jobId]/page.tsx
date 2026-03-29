import JobProgress from "@/components/job-progress";

export default async function JobPage({ params }: { params: Promise<{ jobId: string }> }) {
  const { jobId } = await params;

  return (
    <main className="page-shell">
      <section className="hero-card">
        <div className="eyebrow">Live pipeline status</div>
        <h1>Job {jobId}</h1>
        <JobProgress jobId={jobId} />
      </section>
    </main>
  );
}
