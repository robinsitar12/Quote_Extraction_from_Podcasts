"""
Transcribes wav audio files into text using faster-whisper.
"""

import os
from faster_whisper import WhisperModel
from config import WHISPER_MODEL_SIZE


_model = None  # loaded once and reused


def _get_model() -> WhisperModel:
    """
    Loads the whisper model on first use and cache it, so repeated
    calls to transcribe_wav_to_text() don't reload the model from disk every time.
    """
    global _model
    if _model is None:
        _model = WhisperModel(WHISPER_MODEL_SIZE, device="cpu", compute_type="int8")
    return _model


def transcribe_wav_to_text(wav_path: str, txt_folder: str) -> str:
    """
    Transcribe speech in a wav file into text and save it as a .txt file.

    Args:
        wav_path: Path to the wav file to transcribe.
        txt_folder: Folder to save the resulting txt file in.

    Returns:
        Path to the created txt file.
    """
    os.makedirs(txt_folder, exist_ok=True)

    model = _get_model()
    segments, _info = model.transcribe(wav_path)
    full_text = " ".join(segment.text.strip() for segment in segments)

    filename = os.path.splitext(os.path.basename(wav_path))[0]
    txt_path = os.path.join(txt_folder, f"{filename}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(full_text)

    return txt_path