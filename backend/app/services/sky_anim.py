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

def _boost_mask(mask : np.ndarray, mask_gamma: float = 0.75, mask_gain: float = 2.0) -> np.ndarray:
    m = np.clip(mask.astype(np.float32), 0.0, 1.0)
    m = np.power(m, mask_gamma)
    m *= mask_gain

    return np.clip(m, 0.0, 1.0)



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


def _sky_texture(shape, mode="bands", sky_contrast: float = 1.6):
    H, W = shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    if mode == "bands":
        freq = 0.08
        base= 0.5 + 0.5 * np.sin(2.0 * np.pi * freq * xx)
        grad = 0.85 + 0.15 * (1.0 - (yy.astype(np.float32) / max(1, H -1)))
        tex = base * grad
    else:
        y = np.linspace(0.0, 1.0, H, dtype=np.float32)[:, None]
        tex = (0.6 + 0.4 * y)

    tex = np.clip((tex - 0.5) * sky_contrast + 0.5, 0.0, 1.0)
    tex = (255 * np.dstack([tex, tex, tex])).astype(np.uint8)
    return tex

def sky_frames(
    rgb: np.ndarray,
    duration_s: float = 4.0,
    fps: int = 24,
    intensity: float = 0.5,
    hue_bias: float = 0.0,
    feather_px: int = 8,
    sky_speed_px_per_s: float = 12.0, 
    mask_gamma: float = 0.75,
    mask_gain: float = 2.0,
    sky_contrast: float = 1.6,
    sky_mode: str = "bands",
    lighten_only: bool = True,
    debug_dump_mask_path: str | None = None,
):
    
    if rgb.dtype != np.uint8:
        rgb = rgb.clip(0, 255).astype(np.uint8)
    if rgb.ndim == 2:
        rgb = np.stack([rgb] * 3, axis=-1)
    elif rgb.ndim == 3 and rgb.shape[2] == 4:
        rgb = rgb[..., :3]
    
    intensity = float(np.clip(intensity, 0.0, 1.0))
    feather_px = int(max(0, feather_px))

    

    base_rgb = rgb.astype(np.uint8)
    raw_mask = _soft_sky_mask(base_rgb, feather_px=feather_px, hue_bias=hue_bias)
    mask = _boost_mask(raw_mask, mask_gamma=mask_gamma, mask_gain=mask_gain)[..., None]
    
    if debug_dump_mask_path:
        import imageio.v3 as iio
        iio.imwrite(debug_dump_mask_path, (mask[..., 0] * 255).astype(np.uint8))
    
    sky_tex0 = _sky_texture(base_rgb.shape, mode=sky_mode, sky_contrast=sky_contrast)

    total = max(1, int(round(duration_s * fps)))
    logger.info("Total frames=%d fps=%d", total, fps)

    
    for t in range(total):
        shift = int(round((sky_speed_px_per_s * t) / fps))
        sky_tex = np.roll(sky_tex0, shift, axis=1)  # move left→right

        if lighten_only:
            blend_base = np.maximum(base_rgb, sky_tex).astype(np.float32)
        else:
            blend_base = sky_tex.astype(np.float32)

        alpha = float(intensity) * mask  
        out = base_rgb.astype(np.float32) * (1.0 - alpha) + blend_base * alpha
        yield np.clip(out, 0, 255).astype(np.uint8)