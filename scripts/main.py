import os
from datetime import datetime

from scripts.images import generate_image
from scripts.tts import tts_to_wav
from scripts.video import make_clip


def generate_one(prompt: str) -> str:
    os.makedirs("assets/audio", exist_ok=True)
    os.makedirs("assets/images", exist_ok=True)
    os.makedirs("outputs/videos", exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    img_path = f"assets/images/img_{ts}.png"

    audio_path = f"assets/audio/voice_{ts}.wav"

    out_path = f"outputs/videos/video_{ts}.mp4"

    generate_image(prompt, img_path)
    tts_to_wav(prompt, audio_path)

    make_clip(img_path, audio_path, prompt, out_path)

    return out_path


if __name__ == "__main__":
    import sys
    print("FINAL:", generate_one(sys.argv[1]))
