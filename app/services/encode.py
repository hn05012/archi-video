from pathlib import Path
from imageio.v3 import imwrite
import numpy as np

def write_mp4(frames: list[np.ndarray], out_path: Path, fps: int = 24) -> Path:
    arrs = []
    for f in frames:
        if f.dtype != np.uint8:
            f = f.clip(0, 255).astype(np.uint8)
        if f.ndim == 2:
            f = np.stack([f] * 3, axis=-1) 
        arrs.append(f)

    imwrite(out_path.as_posix(), arrs, fps=fps, codec="libx264")
    return out_path