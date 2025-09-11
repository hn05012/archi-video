import math
from typing import List
import numpy as np
from PIL import Image, ImageEnhance


def load_image_rgb(path: str) -> np.ndarray:
    return np.array(Image.open(path).convert("RGB"), dtype=np.uint8)

def static_video_frames(img_rgb: np.ndarray, total_frames: int) -> List[np.ndarray]:
    return [img_rgb.copy() for _ in range(total_frames)]

def light_pulse_frames(
    img_rgb: np.ndarray,
    total_frames: int,
    fps: int,
    amplitude: float = 0.03,
    period_s: float = 6.0
) -> List[np.ndarray]:
    frames: List[np.ndarray] = []
    base = Image.fromarray(img_rgb)
    hz = 1.0 / period_s if period_s > 0 else 0.0
    for n in range(total_frames):
        t = n / fps
        factor = 1.0 + amplitude * math.cos(2 * math.pi * hz * t)
        enhancer = ImageEnhance.Brightness(base)
        out = ImageEnhance.Brightness(base).enhance(factor)
        frames.append(np.array(out, dtype=np.uint8))

    return frames