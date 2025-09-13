from __future__ import annotations
import io
import math
from typing import Tuple
import numpy as np
from PIL import Image, ImageOps
import imageio.v3 as iio
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

logger = logging.getLogger("sky_anim")

def _np_from_pil(img: Image.Image) -> np.ndarray:
    if img.mode != "RGB":
        img = img.convert("RGB")
    return np.array(img, dtype=np.uint8)

def _pil_from_np(arr: np.ndarray) -> Image.Image:
    return Image.fromarray(arr.astype(np.uint8), mode="RGB")

def _soft_sky_mask(rgb: np.ndarray, feather_px: int = 8, hue_bias: float = 0.0) -> np.ndarray:
    rgb_f = rgb.astype(np.float32) / 255.0
    r, g, b = rgb_f[..., 0], rgb_f[..., 1], rgb_f[..., 2]
    maxc = np.max(rgb_f, axis=-1)
    minc = np.min(rgb_f, axis=-1)
    v= maxc
    saturation = np.where(maxc == 0, 0.0, (maxc - minc) / (maxc + 1e-6))
    hue = np.zeros_like(maxc)
    mask = (maxc != minc)

    rc = (maxc - r) / (maxc - minc + 1e-6)
    gc = (maxc - g) / (maxc - minc + 1e-6)
    bc = (maxc - b) / (maxc - minc + 1e-6)  

    hue = np.where((maxc == r) & mask, (bc - gc), hue)
    hue = np.where((maxc == g) & mask, 2.0 + (rc - bc), hue)
    hue = np.where((maxc == b) & mask, 4.0 + (gc - rc), hue)
    hue = (hue / 6.0) % 1.0

    center = 0.61 + 0.06 * hue_bias
    width = 0.20

    dist = np.minimum(np.abs(hue - center), 1.0 - np.abs(hue - center))
    hue_score = np.clip(1.0 - dist / width, 0.0, 1.0)

    brightness_score = np.clip((v - 0.5) / 0.5, 0.0, 1.0)
    desaturation_score = 1.0 - np.clip((saturation - 0.2)/ 0.6, 0.0, 1.0)

    base = hue_score * 0.6 +  brightness_score * 0.3 + desaturation_score * 0.1
    base = np.clip(base, 0.0, 1.0)

    if feather_px > 0:
        for axis in (0, 1):
            for _ in range(2):
                base = (np.roll(base, 1, axis = axis) + base + np.roll(base, -1, axis = axis)) / 3.0
        base = np.clip(base, 0.0, 1.0)
    
    return base

def _generate_sky_texture(
        size: Tuple[int, int], t: float, intensity: float, *,
    speed: float = 1.2,        
        density: float = 1.4,       
        vertical_wobble: float = 0.25,  
        lighten_only: bool = True   
    )    -> np.ndarray:
    h, w = size
    y = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    top    = np.array([[[180, 205, 255]]], dtype=np.float32) / 255.0  
    bottom = np.array([[[ 80, 140, 220]]], dtype=np.float32) / 255.0  
    base = y[:, None, :] * bottom + (1.0 - y[:, None, :]) * top      
    base = np.broadcast_to(base, (h, w, 3))   


    xs = density * np.linspace(0, 2*np.pi, w, dtype=np.float32)[None, :]  
    yg = np.linspace(0, 1, h, dtype=np.float32)[:, None]               
    
    phase = xs + speed * t + vertical_wobble * (2.0 * np.pi * yg)    

    bands = (
        0.6 * np.sin(phase)
        + 0.3 * np.sin(2.1 * phase + 0.7)
        + 0.1 * np.sin(3.7 * phase - 1.3)
    )

    bands = 0.5 * (bands + 1.0)  

    if lighten_only:
        
        delta = np.maximum(0.0, bands - 0.5)
    else:
        
        delta = (bands - 0.5)

    mod = 1.0 + (intensity * 0.25) * delta  
    sky = np.clip(base * mod[..., None], 0.0, 1.0)  

    return (sky * 255.0 + 0.5).astype(np.uint8)


def sky_frames(
    image: np.ndarray,
    duration_s: float = 4.0,
    fps: int = 24,
    intensity: float = 0.5,
    hue_bias: float = 0.0,
    feather_px: int = 8,
) -> np.ndarray:
    
    if image.dtype != np.uint8:
        image = image.clip(0, 255).astype(np.uint8)
    if image.ndim == 2:
        image = np.stack([image] * 3, axis=-1)
    elif image.ndim == 3 and image.shape[2] == 4:
        image = image[..., :3]
    
    intensity = float(np.clip(intensity, 0.0, 1.0))
    feather_px = int(max(0, feather_px))

    rgb = image
    h, w, _ = rgb.shape

    mask = _soft_sky_mask(rgb, feather_px=feather_px, hue_bias=hue_bias)

    sky_alpha = np.clip(mask * 1.15 - 0.05, 0.0, 1.0)
    fg_alpha = 1.0 - sky_alpha
    fg = rgb.astype(np.float32) / 255.0

    num_frames = int(round(duration_s * fps))
    t_values = np.linspace(0, 2 * np.pi, num_frames, endpoint=False)

    frames = []
    for t in t_values:
        sky = _generate_sky_texture(
            (h, w), t=t, intensity=intensity,
            speed=1.1,          # try 1.0–1.4
            density=1.6,        # 1.2–1.8 gives thinner, less “slab” look
            vertical_wobble=0.3,# 0.2–0.35 adds natural bend
            lighten_only=True   # prevents “gray sheet” feel
        ).astype(np.float32) / 255.0

        comp = sky * sky_alpha[..., None] + fg * fg_alpha[..., None]
        frame = (np.clip(comp, 0.0, 1.0) * 255.0 + 0.5).astype(np.uint8)
        frames.append(frame)

    return frames