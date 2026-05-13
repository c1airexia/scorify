import { useCallback, useRef, useState } from "react";

const API_URL = "http://localhost:8000";

interface UploadResult {
  job_id: string;
  filename: string;
  size_mb: number;
}

interface Props {
  onJobCreated: (result: UploadResult) => void;
}

export default function UploadForm({ onJobCreated }: Props) {
  const [mode, setMode] = useState<"file" | "url">("file");
  const [url, setUrl] = useState("");
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const submit = useCallback(
    async (file?: File) => {
      setError(null);
      setUploading(true);

      try {
        const body = new FormData();
        if (file) {
          body.append("file", file);
        } else {
          body.append("url", url);
        }

        const res = await fetch(`${API_URL}/jobs`, { method: "POST", body });
        const data = await res.json();

        if (!res.ok) {
          throw new Error(data.detail || "Upload failed");
        }

        onJobCreated(data);
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : "Something went wrong");
      } finally {
        setUploading(false);
      }
    },
    [url, onJobCreated]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) {
        setFileName(file.name);
        submit(file);
      }
    },
    [submit]
  );

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) {
        setFileName(file.name);
        submit(file);
      }
    },
    [submit]
  );

  return (
    <div className="upload-form">
      <div className="mode-tabs">
        <button
          className={mode === "file" ? "active" : ""}
          onClick={() => setMode("file")}
          disabled={uploading}
        >
          Upload File
        </button>
        <button
          className={mode === "url" ? "active" : ""}
          onClick={() => setMode("url")}
          disabled={uploading}
        >
          YouTube URL
        </button>
      </div>

      {mode === "file" ? (
        <div
          className={`drop-zone ${dragging ? "dragging" : ""}`}
          onDragOver={(e) => {
            e.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
          onClick={() => fileRef.current?.click()}
        >
          <input
            ref={fileRef}
            type="file"
            accept=".mp3,.wav,.m4a,.flac,.ogg"
            onChange={handleFileSelect}
            hidden
          />
          {uploading ? (
            <p>Uploading {fileName}...</p>
          ) : (
            <p>Drag & drop an audio file here, or click to browse</p>
          )}
          <span className="hint">MP3, WAV, M4A, FLAC, OGG &mdash; max 50 MB</span>
        </div>
      ) : (
        <form
          className="url-form"
          onSubmit={(e) => {
            e.preventDefault();
            submit();
          }}
        >
          <input
            type="url"
            placeholder="https://www.youtube.com/watch?v=..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            disabled={uploading}
          />
          <button type="submit" disabled={uploading || !url.trim()}>
            {uploading ? "Downloading..." : "Download"}
          </button>
        </form>
      )}

      {error && <p className="error">{error}</p>}
    </div>
  );
}
