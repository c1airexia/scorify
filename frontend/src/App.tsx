import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://localhost:8000";

function App() {
  const [health, setHealth] = useState<{
    status: string;
    version: string;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/health`)
      .then((res) => res.json())
      .then(setHealth)
      .catch(() => setError("Cannot connect to backend. Is the server running?"));
  }, []);

  return (
    <div className="app">
      <header>
        <h1>Scorify</h1>
        <p className="subtitle">Piano sheet music from any song</p>
      </header>

      <main>
        <div className="status-card">
          {error && <p className="error">{error}</p>}
          {health && (
            <p className="connected">
              Backend connected &mdash; v{health.version}
            </p>
          )}
          {!health && !error && <p className="loading">Connecting to backend...</p>}
        </div>
      </main>
    </div>
  );
}

export default App;
