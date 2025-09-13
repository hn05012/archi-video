import os
import uuid
from pathlib import Path
from fastapi import UploadFile
from PIL import Image
import numpy as np

UPLOAD_DIR = Path("data/uploads")
OUTPUT_DIR = Path("data/outputs")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def save_upload(file: UploadFile) -> Path:
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in {".jpg", ".jpeg", ".png", ".bmp"}:
        ext = ".png"
    name = f"{uuid.uuid4().hex}{ext}"
    Path = UPLOAD_DIR / name

    with Path.open("wb") as f:
        f.write(file.file.read())
    return Path

def make_output_path(suffix: str = "mp4") -> Path:
    return OUTPUT_DIR / f"{uuid.uuid4().hex}.{suffix}"

def ensure_max_width(arr: np.ndarray, max_w: int = 1280) -> np.ndarray:
    if arr.shape[1] <= max_w:  # arr.shape = (H, W, 3)
        return arr
    pil_img = Image.fromarray(arr)
    new_h = int(round(arr.shape[0] * (max_w / arr.shape[1])))
    pil_resized = pil_img.resize((max_w, new_h), Image.LANCZOS)
    return np.array(pil_resized, dtype=np.uint8)
