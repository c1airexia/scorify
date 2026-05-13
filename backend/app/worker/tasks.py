import logging
from pathlib import Path

from app.worker.celery_app import celery

log = logging.getLogger(__name__)


@celery.task(bind=True, name="transcribe")
def transcribe_task(self, job_id: str):
    """Run the full transcription pipeline for a job.

    Currently implements: Demucs piano stem separation.
    Stages 4-5 will add Basic Pitch and music21 processing.
    """
    from app.config import settings

    job_dir = settings.upload_dir / job_id
    input_files = list(job_dir.glob("input.*"))
    if not input_files:
        raise FileNotFoundError(f"No input audio found for job {job_id}")

    input_path = input_files[0]

    # --- Step 1: Demucs stem separation ---
    self.update_state(
        state="PROGRESS",
        meta={"step": "separating", "detail": "Isolating piano stem...", "progress": 0.1},
    )

    from app.pipeline.separate import separate_piano

    piano_path = separate_piano(input_path, job_dir)

    # --- Step 2: Basic Pitch note detection ---
    self.update_state(
        state="PROGRESS",
        meta={"step": "transcribing", "detail": "Detecting notes...", "progress": 0.5},
    )

    from app.pipeline.transcribe import audio_to_midi

    midi_path = audio_to_midi(piano_path, job_dir)

    # --- Step 3: music21 processing (Stage 5 placeholder) ---
    self.update_state(
        state="PROGRESS",
        meta={"step": "processing", "detail": "Building sheet music...", "progress": 0.8},
    )

    result = {
        "step": "done",
        "detail": "Transcription complete",
        "progress": 1.0,
        "piano_stem": str(piano_path),
        "midi_file": str(midi_path),
    }
    log.info("Job %s completed: %s", job_id, result)
    return result
