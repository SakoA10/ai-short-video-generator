import os
import random
import urllib.request
from PIL import Image

W = 1080
H = 1920

def _ensure_dirs():
    os.makedirs("assets/images", exist_ok=True)
    os.makedirs("assets/backgrounds", exist_ok=True)

def _download_random_photo(out_path: str):
    seed = random.randint(1, 10_000_000)
    url = f"https://picsum.photos/seed/{seed}/{W}/{H}"
    urllib.request.urlretrieve(url, out_path)

def generate_image(sentence: str, out_path: str):
    
    _ensure_dirs()

    bg_path = os.path.join(
        "assets",
        "backgrounds",
        f"bg_{random.randint(1000,9999)}.jpg"
    )

    _download_random_photo(bg_path)

    img = Image.open(bg_path).convert("RGB")
    img.save(out_path)
