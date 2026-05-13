import logging
from pathlib import Path

import torch
import torchaudio

log = logging.getLogger(__name__)

_model = None


def _get_model():
    """Lazy-load the Demucs model so it's only downloaded/loaded once."""
    global _model
    if _model is None:
        from demucs.pretrained import get_model

        log.info("Loading Demucs htdemucs_6s model...")
        _model = get_model("htdemucs_6s")
        _model.eval()
        log.info("Demucs model loaded. Sources: %s", _model.sources)
    return _model


def separate_piano(input_path: Path, output_dir: Path) -> Path:
    """Isolate the piano stem from an audio file using Demucs.

    Returns the path to the piano stem WAV file.
    """
    from demucs.apply import apply_model
    from demucs.audio import AudioFile

    model = _get_model()

    log.info("Separating stems from %s (this may take several minutes on CPU)...", input_path.name)

    wav = AudioFile(input_path).read(streams=0, samplerate=model.samplerate, channels=model.audio_channels)
    ref = wav.mean(0)
    wav = (wav - ref.mean()) / ref.std()

    with torch.no_grad():
        sources = apply_model(model, wav[None], device="cpu")[0]

    sources = sources * ref.std() + ref.mean()

    piano_idx = model.sources.index("piano")
    piano_stem = sources[piano_idx]

    out_path = output_dir / "piano.wav"
    torchaudio.save(str(out_path), piano_stem.cpu(), sample_rate=model.samplerate)

    log.info("Piano stem saved to %s (%.1f MB)", out_path, out_path.stat().st_size / 1e6)
    return out_path
