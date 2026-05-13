from __future__ import annotations

import shutil
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.config import settings
from app.pipeline.download import download_audio, is_youtube_url

router = APIRouter(prefix="/jobs", tags=["jobs"])

ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".flac", ".ogg"}


@router.post("", status_code=202)
async def create_job(
    file: Optional[UploadFile] = File(None),
    url: Optional[str] = Form(None),
):
    """Accept an audio file upload or a YouTube URL, then start processing."""
    if not file and not url:
        raise HTTPException(status_code=400, detail="Provide either a file or a YouTube URL")

    if file and url:
        raise HTTPException(status_code=400, detail="Provide a file or a URL, not both")

    job_id = uuid.uuid4().hex
    job_dir = settings.upload_dir / job_id
    job_dir.mkdir(parents=True)

    try:
        if file:
            audio_path = _save_upload(file, job_dir)
        else:
            audio_path = _download_url(url, job_dir)
    except Exception as e:
        shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(status_code=400, detail=str(e))

    from app.worker.tasks import transcribe_task

    task = transcribe_task.delay(job_id)

    task_id_file = job_dir / ".task_id"
    task_id_file.write_text(task.id)

    return {
        "job_id": job_id,
        "task_id": task.id,
        "filename": audio_path.name,
        "size_mb": round(audio_path.stat().st_size / 1e6, 2),
    }


def _save_upload(file: UploadFile, job_dir: Path) -> Path:
    ext = Path(file.filename or "audio.wav").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")

    size = 0
    max_bytes = settings.max_upload_mb * 1024 * 1024
    dest = job_dir / f"input{ext}"

    with open(dest, "wb") as f:
        while chunk := file.file.read(1024 * 1024):
            size += len(chunk)
            if size > max_bytes:
                raise ValueError(f"File too large (max {settings.max_upload_mb} MB)")
            f.write(chunk)

    return dest


def _download_url(url: str, job_dir: Path) -> Path:
    if not is_youtube_url(url):
        raise ValueError(
            "Only YouTube URLs are supported. "
            "Spotify URLs cannot be downloaded — upload the audio file directly instead."
        )
    return download_audio(url, job_dir)


@router.get("/{job_id}")
async def get_job_status(job_id: str):
    """Check the status of a transcription job by reading Celery task state."""
    job_dir = settings.upload_dir / job_id
    if not job_dir.exists():
        raise HTTPException(status_code=404, detail="Job not found")

    task_id_file = job_dir / ".task_id"
    if not task_id_file.exists():
        return {"job_id": job_id, "status": "uploaded", "progress": 0, "step": "queued"}

    from app.worker.celery_app import celery

    task_id = task_id_file.read_text().strip()
    result = celery.AsyncResult(task_id)

    if result.state == "PENDING":
        return {"job_id": job_id, "status": "pending", "progress": 0, "step": "queued", "detail": "Waiting for worker..."}
    elif result.state == "STARTED":
        return {"job_id": job_id, "status": "started", "progress": 0.05, "step": "starting", "detail": "Worker picked up job..."}
    elif result.state == "PROGRESS":
        info = result.info or {}
        return {
            "job_id": job_id,
            "status": "processing",
            "progress": info.get("progress", 0),
            "step": info.get("step", "unknown"),
            "detail": info.get("detail", ""),
        }
    elif result.state == "SUCCESS":
        return {
            "job_id": job_id,
            "status": "completed",
            "progress": 1.0,
            "step": "done",
            "detail": "Processing complete",
            "result": result.result,
        }
    elif result.state == "FAILURE":
        return {
            "job_id": job_id,
            "status": "failed",
            "progress": 0,
            "step": "error",
            "detail": str(result.result),
        }
    else:
        return {"job_id": job_id, "status": result.state.lower(), "progress": 0, "step": "unknown"}
