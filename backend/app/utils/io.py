import os
import uuid
from pathlib import Path
from fastapi import UploadFile



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


