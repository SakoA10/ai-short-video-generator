import os
import sys
import uuid
import random
import shutil
import subprocess


def tts_to_wav(text: str, out_wav_path: str) -> str:
    """
    High-quality AI voice using Microsoft Edge Neural TTS.
    Uses: python -m edge_tts  (so it works even when PATH is different in n8n/uvicorn)
    """

    os.makedirs(os.path.dirname(out_wav_path), exist_ok=True)

    voices = "en-US-JennyNeural",
    voice = random.choice(voices)

    tmp_mp3 = os.path.join(os.path.dirname(out_wav_path), f"tmp_{uuid.uuid4().hex}.mp3")

    # 1) Generate MP3 via edge-tts (using venv python)
    cmd_tts = [
        sys.executable, "-m", "edge_tts",
        "--voice", voice,
        "--text", text,
        "--write-media", tmp_mp3,
    ]
    subprocess.run(cmd_tts, check=True)

    # 2) Convert MP3 -> WAV (ffmpeg must be available)
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise FileNotFoundError(
            "ffmpeg not found in PATH. Install ffmpeg or add it to PATH, then restart VS Code/terminal."
        )

    subprocess.run([ffmpeg, "-y", "-i", tmp_mp3, out_wav_path], check=True)

    try:
        os.remove(tmp_mp3)
    except:
        pass

    return out_wav_path
