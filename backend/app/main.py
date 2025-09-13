import io
import logging
import time
import uuid
from app.logging_setup import RequestIDFilter, request_id_var
from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form
from PIL import Image
from fastapi.responses import JSONResponse
from app.utils.io import ensure_max_width, save_upload, make_output_path
from app.services.presets import load_image_rgb, static_video_frames, light_pulse_frames
from app.services.encode import write_mp4
from app.services.sky_anim import sky_frames



RequestIDFilter.setup_Logging("INFO")

logger = logging.getLogger("app.main")

app = FastAPI(title="Image to Video API")


@app.get("/health")
async def health_check():
    return JSONResponse(content={"status": "ok"})




@app.middleware("http")
async def add_request_id_and_timing(request: Request, call_next):
    rid = str(uuid.uuid4())
    token = request_id_var.set(rid)
    start = time.perf_counter()

    try:
        logger.info(f"Start request {request.method} {request.url.path}")
        response = await call_next(request)
        return response
    except Exception:
        logger.exception("Unhandled exception")
        raise
    finally:
        duration = (time.perf_counter() - start) * 1000
        logger.info(f"Completed request {request.method} {request.url.path} in {duration:.2f}ms")
        request_id_var.reset(token)


@app.post("/video/static")
async def video_static(file: UploadFile = File(...),
    duration_s: float = Form(8.0),
    fps: int = Form(24),
):  
    path = save_upload(file)
    image = load_image_rgb(path)
    total_frames = max(1, int(duration_s * fps))
    frames = static_video_frames(image, total_frames)
    out_path = make_output_path("mp4")
    write_mp4(frames, out_path, fps)
    return JSONResponse(content={"video_path": str(out_path)})

@app.post("/video/light")
async def video_light(
    file: UploadFile = File(...),
    duration_s: float = Form(8.0),
    fps: int = Form(24),
    amplitude: float = Form(0.03),
    period_s: float = Form(6.0)
):  
    path = save_upload(file)
    image = load_image_rgb(path)
    total_frames = max(1, int(duration_s * fps))
    frames = light_pulse_frames(image, total_frames, fps, amplitude, period_s)
    out_path = make_output_path("mp4")
    write_mp4(frames, out_path, fps)
    return JSONResponse(content={"video_path": str(out_path)})


@app.post("/video/sky")
async def video_sky(
    file: UploadFile = File(...),
    duration_s: float = Form(4.0),
    fps: int = Form(24),
    intensity: float = Form(0.4),
    hue_bias: float = Form(0.0),
    feather_px: int = Form(8),
):
    
    try:
        path = save_upload(file)
        logger.info(f"Saved upload to {path}")
        
        image = load_image_rgb(path)
        logger.info("Loaded image shape=%s dtype=%s", getattr(image, 'shape', "?"), getattr(image, 'dtype', "?"))
        
        image = ensure_max_width(image, 1280)
        logger.info("Resized (if needed) image shape=%s", getattr(image, 'shape', "?"))
        frames = sky_frames(
            rgb = image,
            duration_s=duration_s,
            fps=fps,
            intensity=intensity,
            hue_bias=hue_bias,
            feather_px=feather_px,
            sky_speed_px_per_s=20.0, 
            mask_gamma=0.75,
            mask_gain=2.0,
            sky_contrast=1.6,
            sky_mode="bands",
            lighten_only=True,
        )

        logger.info("Generated sky frames")

        out_path = make_output_path("mp4")
        logger.info(f"Writing output video to {out_path}")

        write_mp4(frames, out_path, fps)
        logger.info("Finished writing video")

        return JSONResponse(content={"video_path": str(out_path)})

    except Exception as e:
        logger.exception("video_sky failed")
        raise HTTPException(status_code=500, detail=str(e))

