import logging
import os
import shutil
import subprocess
from pathlib import Path

log = logging.getLogger(__name__)

ALLOWED_DOMAINS = {"youtube.com", "www.youtube.com", "youtu.be", "m.youtube.com"}

# nvm-managed Node isn't in PATH for subprocesses; find it once at import time
_NODE_PATH = shutil.which("node") or os.path.expanduser(
    "~/.nvm/versions/node/v20.19.6/bin/node"
)


def is_youtube_url(url: str) -> bool:
    from urllib.parse import urlparse

    try:
        parsed = urlparse(url)
        return parsed.hostname in ALLOWED_DOMAINS
    except Exception:
        return False


def download_audio(url: str, output_dir: Path) -> Path:
    """Download audio from a YouTube URL and convert to WAV.

    Returns the path to the downloaded WAV file.
    Raises RuntimeError if the download fails.
    """
    output_path = output_dir / "input.wav"
    output_template = str(output_dir / "input.%(ext)s")

    cmd = [
        "yt-dlp",
        "--extract-audio",
        "--audio-format", "wav",
        "--output", output_template,
        "--no-playlist",
        "--no-overwrites",
        "--extractor-args", "youtube:player_client=web_music",
        "--js-runtimes", f"node:{_NODE_PATH}",
        url,
    ]

    env = {**os.environ, "PATH": str(Path(_NODE_PATH).parent) + ":" + os.environ.get("PATH", "")}
    log.info("Downloading audio from %s", url)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, env=env)

    if result.returncode != 0:
        log.error("yt-dlp failed: %s", result.stderr)
        raise RuntimeError(f"Failed to download audio: {result.stderr[:500]}")

    if not output_path.exists():
        raise RuntimeError("Download completed but WAV file not found")

    log.info("Downloaded audio to %s (%.1f MB)", output_path, output_path.stat().st_size / 1e6)
    return output_path
