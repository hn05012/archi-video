from __future__ import annotations
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
import io

from app.services.i2v_worker import create_job, get_job, model_loaded

router = APIRouter(prefix="/svd", tags=["svd"])

@router.post("/")
async def start(
    image: UploadFile = File(...),
    frames: int | None = Form(None),
    num_frames: int | None = Form(None),
    fps: int = Form(9),
    max_side: int = Form(320),
    steps: int = Form(6),
    denoise_strength: float = Form(0.4),
    cfg: float = Form(1.0),
    seed: int | None = Form(None)
):
    if frames is None and num_frames is not None:
        frames = int(num_frames)
    frames = frames or 20

    data = await image.read()

    try:
        Image.open(io.BytesIO(data)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail = "invalid image")
    
    frames = int(max(8, min(frames, 28)))
    fps = int(max(6, min(fps, 12)))
    max_side = int(max(256, min(max_side, 512)))
    steps = int(max(2, min(steps, 8)))
    denoise_strength = float(max(0.2, min(denoise_strength, 0.7)))
    cfg = float(max(0.0, min(cfg, 3.0)))

    try:
        job = create_job(
            data,
            frames = frames, fps=fps, max_side=max_side, steps=steps,
            denoise_strength=denoise_strength, cfg = cfg, seed=seed
        )
    except RuntimeError as e:
        raise HTTPException(status_code = 429, detail = str(e))
    
    return {"job_id": job.id, "status": job.status}


@router.get("/status/{job_id}")
def status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code =404, detail = "job not found")
    return {
        "job_id": job.id,
        "status": job.status,
        "progress": {"current": job.current, "total": job.total, "eta_seconds": job.eta_seconds},
        "error": job.error
    }

@router.get("/result/{job_id}")
def result(job_id: str):
    job = get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail = "job not found")
    if job.status != "done":
        raise HTTPException(status_code=409, detail = f"job not ready (status={job.status})")
    
    duration_s = job.params["frames"] / float(job.params["fps"])

    return {
        "job_id": job.id,
        "video_path": f"static/jobs/{job.id}/out.mp4",
        "frames": job.params["frames"],
        "fps": job.params["fps"],
        "duration_s": duration_s,
        "seed": job.params.get("seed"),
        "params": job.params
    }