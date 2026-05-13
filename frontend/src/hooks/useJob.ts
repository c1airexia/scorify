import { useCallback, useEffect, useRef, useState } from "react";

const API_URL = "http://localhost:8000";

export interface JobStatus {
  job_id: string;
  status: string;
  progress: number;
  step: string;
  detail: string;
  result?: Record<string, unknown>;
}

export function useJob(jobId: string | null) {
  const [status, setStatus] = useState<JobStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const stop = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  useEffect(() => {
    if (!jobId) {
      setStatus(null);
      setError(null);
      return;
    }

    const poll = async () => {
      try {
        const res = await fetch(`${API_URL}/jobs/${jobId}`);
        if (!res.ok) throw new Error("Failed to fetch job status");
        const data: JobStatus = await res.json();
        setStatus(data);

        if (data.status === "completed" || data.status === "failed") {
          stop();
        }
      } catch {
        setError("Lost connection to server");
        stop();
      }
    };

    poll();
    intervalRef.current = setInterval(poll, 2000);

    return stop;
  }, [jobId, stop]);

  return { status, error };
}
