from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}")
async def get_job_status(job_id: str):
    """Check the status of a transcription job. (Wired up in Stage 3.)"""
    raise HTTPException(status_code=501, detail="Job processing not yet implemented")
