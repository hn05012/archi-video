from fastapi import FastAPI, UploadFile, File, Form

from fastapi.responses import JSONResponse
from app.utils.io import save_upload, make_output_path
from app.services.presets import load_image_rgb, static_video_frames, light_pulse_frames
from app.services.encode import write_mp4
app = FastAPI(title="Image to Video API")


@app.get("/health")
async def health_check():
    return JSONResponse(content={"status": "ok"})

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



