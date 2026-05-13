from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    redis_url: str = "redis://localhost:6379/0"
    upload_dir: Path = Path(__file__).resolve().parent.parent / "uploads"
    max_upload_mb: int = 50

    model_config = {"env_prefix": "SCORIFY_"}


settings = Settings()
settings.upload_dir.mkdir(parents=True, exist_ok=True)
