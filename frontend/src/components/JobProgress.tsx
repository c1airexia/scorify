import { useJob } from "../hooks/useJob";

const STEP_LABELS: Record<string, string> = {
  queued: "Queued",
  starting: "Starting worker...",
  separating: "Isolating piano stem...",
  transcribing: "Detecting notes...",
  processing: "Building sheet music...",
  done: "Complete!",
  error: "Failed",
};

interface Props {
  jobId: string;
  onComplete: (result: Record<string, unknown>) => void;
}

export default function JobProgress({ jobId, onComplete }: Props) {
  const { status, error } = useJob(jobId);

  if (error) {
    return <div className="progress-card error-card"><p>{error}</p></div>;
  }

  if (!status) {
    return <div className="progress-card"><p>Starting...</p></div>;
  }

  if (status.status === "completed" && status.result) {
    onComplete(status.result);
  }

  const pct = Math.round(status.progress * 100);
  const label = STEP_LABELS[status.step] || status.detail || status.step;

  return (
    <div className="progress-card">
      <p className="progress-label">{label}</p>
      <div className="progress-bar-track">
        <div
          className="progress-bar-fill"
          style={{ width: `${pct}%` }}
        />
      </div>
      <p className="progress-pct">{pct}%</p>
      {status.status === "failed" && (
        <p className="error">{status.detail}</p>
      )}
    </div>
  );
}
