"""
Converts downloaded mp3 podcast episodes into wav files for transcription.
My code is inspired by the following documentation: "https://pythonbasics.org/convert-mp3-to-wav/"
"""

import os
from pydub import AudioSegment


def convert_mp3_to_wav(mp3_path: str, wav_folder: str) -> str:
    """
    Convert a single mp3 file into a wav file

    Args:
        mp3_path: Path to the source mp3 file.
        wav_folder: Folder to save the resulting wav file in.

    Returns:
        Path to the created wav file.
    """
    os.makedirs(wav_folder, exist_ok=True)

    mp3_audio = AudioSegment.from_file(mp3_path, format="mp3")
    wav_audio = mp3_audio.set_frame_rate(44100).set_channels(1)

    filename = os.path.splitext(os.path.basename(mp3_path))[0]
    wav_path = os.path.join(wav_folder, f"{filename}.wav")
    wav_audio.export(wav_path, format="wav")

    return wav_path