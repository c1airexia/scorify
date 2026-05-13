import logging
from pathlib import Path

log = logging.getLogger(__name__)


def audio_to_midi(audio_path: Path, output_dir: Path) -> Path:
    """Convert an audio file to MIDI using Spotify's Basic Pitch.

    Returns the path to the generated MIDI file.
    """
    from basic_pitch import build_icassp_2022_model_path, FilenameSuffix
    from basic_pitch.inference import predict

    log.info("Running Basic Pitch on %s...", audio_path.name)

    onnx_model_path = build_icassp_2022_model_path(FilenameSuffix.onnx)
    _model_output, midi_data, _note_events = predict(
        str(audio_path),
        model_or_model_path=onnx_model_path,
    )

    midi_path = output_dir / "piano.mid"
    midi_data.write(str(midi_path))

    log.info("MIDI saved to %s", midi_path)
    return midi_path
