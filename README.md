# Scorify

Piano sheet music from any song. Upload an audio file and Scorify transcribes it into readable sheet music rendered right in the browser.

## Architecture

```
frontend/          React + TypeScript (Vite)
backend/
  app/
    api/           FastAPI REST endpoints
    worker/        Celery task queue (Redis broker)
    pipeline/      Audio → MIDI → score processing (coming soon)
```

**Frontend** — React 19, TypeScript, VexFlow for music notation rendering.

**Backend** — FastAPI serving a REST API with a Celery worker for long-running transcription jobs. Redis is used as the message broker and result backend.

## Prerequisites

- Python 3.9+
- Node.js 18+
- Redis (for the Celery task queue)

## Getting Started

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`. Visit `/docs` for the interactive Swagger UI.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The dev server starts at `http://localhost:5173` and proxies health checks to the backend.

### Celery Worker (optional for now)

```bash
cd backend
source .venv/bin/activate
celery -A app.worker.celery_app worker --loglevel=info
```

## Configuration

Backend settings are managed via environment variables prefixed with `SCORIFY_`:

| Variable | Default | Description |
|---|---|---|
| `SCORIFY_REDIS_URL` | `redis://localhost:6379/0` | Redis connection string |
| `SCORIFY_UPLOAD_DIR` | `backend/uploads/` | Directory for uploaded audio files |
| `SCORIFY_MAX_UPLOAD_MB` | `50` | Maximum upload size in MB |

## Roadmap

- **Stage 1** — Project scaffold, frontend/backend wiring *(done)*
- **Stage 2** — File upload UI and API endpoint
- **Stage 3** — Audio-to-MIDI transcription pipeline
- **Stage 4** — MIDI-to-score rendering with VexFlow
- **Stage 5** — Polish, export, and deployment

## License

MIT
