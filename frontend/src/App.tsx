import { useEffect, useRef, useState } from "react";
import UploadForm from "./components/UploadForm";
import JobProgress from "./components/JobProgress";
import "./App.css";

const API_URL = "http://localhost:8000";

function App() {
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [done, setDone] = useState(false);
  const completedRef = useRef(false);

  useEffect(() => {
    fetch(`${API_URL}/health`)
      .then((res) => res.json())
      .then(() => setConnected(true))
      .catch(() => setError("Cannot connect to backend. Is the server running?"));
  }, []);

  const handleJobCreated = (result: { job_id: string }) => {
    completedRef.current = false;
    setDone(false);
    setJobId(result.job_id);
  };

  const handleComplete = (_result: Record<string, unknown>) => {
    if (!completedRef.current) {
      completedRef.current = true;
      setDone(true);
    }
  };

  const reset = () => {
    setJobId(null);
    setDone(false);
    completedRef.current = false;
  };

  return (
    <div className="app">
      <header>
        <h1>Scorify</h1>
        <p className="subtitle">Piano sheet music from any song</p>
      </header>

      <main>
        {error && <p className="error">{error}</p>}

        {connected && !jobId && <UploadForm onJobCreated={handleJobCreated} />}

        {jobId && !done && (
          <JobProgress jobId={jobId} onComplete={handleComplete} />
        )}

        {done && (
          <div className="status-card success">
            <p>Piano stem separated!</p>
            <p className="detail">
              The piano track has been isolated from the audio.
              Next stages will detect notes and render sheet music.
            </p>
            <button className="new-job-btn" onClick={reset}>
              Upload another
            </button>
          </div>
        )}

        {!connected && !error && (
          <p className="loading">Connecting to backend...</p>
        )}
      </main>
    </div>
  );
}

export default App;
