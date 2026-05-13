import { useEffect, useState } from "react";
import UploadForm from "./components/UploadForm";
import "./App.css";

const API_URL = "http://localhost:8000";

function App() {
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [jobResult, setJobResult] = useState<{
    job_id: string;
    filename: string;
    size_mb: number;
  } | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/health`)
      .then((res) => res.json())
      .then(() => setConnected(true))
      .catch(() => setError("Cannot connect to backend. Is the server running?"));
  }, []);

  return (
    <div className="app">
      <header>
        <h1>Scorify</h1>
        <p className="subtitle">Piano sheet music from any song</p>
      </header>

      <main>
        {error && <p className="error">{error}</p>}

        {connected && !jobResult && (
          <UploadForm onJobCreated={setJobResult} />
        )}

        {jobResult && (
          <div className="status-card success">
            <p>Audio received!</p>
            <table>
              <tbody>
                <tr>
                  <td>Job ID</td>
                  <td><code>{jobResult.job_id}</code></td>
                </tr>
                <tr>
                  <td>File</td>
                  <td>{jobResult.filename}</td>
                </tr>
                <tr>
                  <td>Size</td>
                  <td>{jobResult.size_mb} MB</td>
                </tr>
              </tbody>
            </table>
            <button
              className="new-job-btn"
              onClick={() => setJobResult(null)}
            >
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
