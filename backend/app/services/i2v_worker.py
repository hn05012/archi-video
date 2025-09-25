from __future__ import annotations
import io, os, time, json, uuid, threading, queue
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

from app.services.encode import write_mp4
from pathlib import Path
import numpy as np
from PIL import Image
import torch


from diffusers import (
    AnimateDiffVideoToVideoPipeline,
    MotionAdapter,
    LCMScheduler
)
APP_DIR = Path(__file__).resolve().parents[1]          
OUTPUTS_ROOT = APP_DIR / "data" / "outputs"            
DATA_DIR = Path(os.getenv("DATA_DIR", OUTPUTS_ROOT / "jobs"))

DATA_DIR.mkdir(parents=True, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

MAX_QUEUE=int(os.getenv("MAX_QUEUE", "2"))
JOB_TTL_H=int(os.getenv("JOB_TTL_H", "2"))

def _init_threads():
    default_threads = max(1, min(os.cpu_count() or 4, 6))
    os.environ.setdefault("OMP_NUM_THREADS", str(default_threads))
    os.environ.setdefault("MKL_NUM_THREADS", str(default_threads))
    torch.set_num_threads(int(os.environ.get("TORCH_NUM_THREADS", default_threads)))
    torch.set_num_interop_threads(int(os.environ.get("TORCH_NUM_INTEROP", 1)))
    
_init_threads()

@dataclass
class Job: 
    id: str
    status: str
    created_ts: float
    started_ts: Optional[float] = None
    finished_ts: Optional[float] = None
    error: Optional[str] = None
    current: int = 0
    total: int = 0
    eta_seconds: Optional[float] = None
    params: Dict = None
    job_dir: str = ""
    input_path: str = ""
    frames_dir: str = ""
    video_path: str = ""


class ModelManager:
    _lock = threading.Lock()
    _pipe: Optional[AnimateDiffVideoToVideoPipeline] = None
    _loaded = False

    @classmethod
    def get_pipe(cls) -> AnimateDiffVideoToVideoPipeline:
        with cls._lock:
            if cls._pipe is None:
                cls._pipe = cls._load_pipeline()
                cls._loaded = True
            return cls._pipe
    
    @staticmethod
    def _load_pipeline() -> AnimateDiffVideoToVideoPipeline:
        motion_adapter_id = os.getenv("MOTION_ADAPTER_ID", "guoyww/animatediff-motion-adapter-v1-5")
        base_model_id = os.getenv("BASE_MODEL_ID", "runwayml/stable-diffusion-v1-5")
        lcm_repo = os.getenv("LCM_REPO", "wangfuyun/AnimateLCM")
        lcm_weight_name = os.getenv("LCM_WEIGHT_NAME", "AnimateLCM_sd15_i2v_lora.safetensors")
        lcm_weight = float(os.getenv("LCM_LORA_WEIGHT", "0.8"))

        adapter = MotionAdapter.from_pretrained(motion_adapter_id)
        pipe = AnimateDiffVideoToVideoPipeline.from_pretrained(
            base_model_id,
            motion_adapter = adapter
        )

        pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config, beta_schedule="linear")
        try:
            pipe.load_lora_weights(lcm_repo, weight_name = lcm_weight_name, adapter_name="lcm-lora")
            pipe.set_adapters(["lcm-lora"], [lcm_weight])
        except Exception as e:
            print(f"[ModelManager] WARN: failed to load AnimateLCM LoRA: {e}")

        pipe.enable_attention_slicing()
        pipe.set_progress_bar_config(disable=True)
        pipe.to("cpu")
        return pipe
    
def _load_and_resize_image(data: bytes, max_side: int) -> Image.Image:
    img = Image.open(io.BytesIO(data)).convert("RGB")
    w, h = img.size
    if max(w, h) > max_side:
        if w >= h:
            new_w = max_side
            new_h = int(h * (max_side / w))
        else:
            new_h = max_side
            new_w = int(w * (max_side / h))
        img = img.resize((new_w, new_h), Image.LANCZOS)
    return img

class JobQueue:
    def __init__(self):
        self.q: "queue.Queue[str]" = queue.Queue()
        self.jobs: Dict[str, Job] = {}
        self.lock = threading.Lock()
        self.worker = threading.Thread(target=self._loop, daemon=True)

        self.worker.start()

    def put(self, job: Job):
        with self.lock:
            self.jobs[job.id] = job
        self.q.put(job.id)

    def get(self, job_id: str) -> Optional[Job]:
        with self.lock:
            return self.jobs.get(job_id)
        
    def _estimate_total_seconds(self, frames: int, steps: int, max_side: int) -> float:
        base_s_per_frame = 25
        scale_steps = steps/6.0
        scale_res = (max_side/320.0) ** 2
        return max(1.0, frames*base_s_per_frame*max(0.5, scale_steps) * max(0.5, scale_res)) 
    
    def _loop(self):
        while True:
            job_id = self.q.get()
            job = self.get(job_id)
            if not job:
                continue
            job.status = "running"
            job.started_ts = time.time()

            est_total = self._estimate_total_seconds(job.total, job.params["steps"], job.params["max_side"])
            stop_evt = threading.Event()

            def _tick():
                while not stop_evt.is_set():
                    elapsed = time.time() - (job.started_ts or time.time())
                    frac = min(0.95, elapsed/est_total)
                    job.current = max(1, int(job.total * frac)) if job.total else 0
                    job.eta_seconds = max(0.0, est_total-elapsed)
                    time.sleep(1.0)
            
            t = threading.Thread(target=_tick, daemon=True)
            t.start()


            try:
                self._run_job(job)
                job.status = "done"
                job.finished_ts = time.time()
                job.current = job.total
                job.eta_seconds = 0.0

            except Exception as e:
                job.status = "failed"
                job.error = str(e)
                job.finished_ts = time.time()

            finally:
                stop_evt.set()
                t.join(timeout=0.1)
                self.q.task_done()

    def _run_job(self, job: Job):
        pipe = ModelManager.get_pipe()
        p = job.params

        with open(job.input_path, "rb") as f:
            img = _load_and_resize_image(f.read(), p["max_side"])

        frames_in: List[Image.Image] = [img.copy() for _ in range(p["frames"])]

        generator = torch.Generator(device="cpu")
        if p.get("seed") is not None:
            generator = generator.manual_seed(int(p["seed"]))

        with torch.inference_mode():
            out = pipe(
                video=frames_in,
                prompt=p.get("prompt", ""),
                negative_prompt=p.get("negative_prompt", ""),
                num_inference_steps=p["steps"],
                guidance_scale=p["cfg"],
                strength=p["denoise_strength"],  
                generator=generator,
            )

        frames_out: List[Image.Image] = out.frames[0]

        np_frames = [np.array(fr.convert("RGB"), dtype=np.uint8) for fr in frames_out]
        write_mp4(np_frames, Path(job.video_path), p["fps"])

        job.current = job.total


JOBS = JobQueue()

def create_job(
    file_bytes: bytes,
    *,
    frames: int,
    fps: int,
    max_side: int,
    steps: int,
    denoise_strength: float,
    cfg: float,
    seed: Optional[int]
) -> Job:
    if len(file_bytes) > 12 * 1024 * 1024:
        raise ValueError("image too large (max 12 MB)")
    jid = str(uuid.uuid4())
    job_dir = os.path.join(DATA_DIR, jid)
    frames_dir = os.path.join(job_dir, "frames")
    os.makedirs(frames_dir, exist_ok=True)
    input_path = os.path.join(job_dir, "input.png")
    video_path = os.path.join(job_dir, "out.mp4")

    with open(input_path, "wb") as f:
        f.write(file_bytes)

    params = {
        "frames": frames,
        "fps": fps,
        "max_side": max_side,
        "steps": steps,
        "denoise_strength": denoise_strength,
        "cfg": cfg,
        "seed": seed,
        "prompt": "",
        "negative_prompt": "",
    }

    job = Job(
        id=jid,
        status="QUEUED",
        created_ts=time.time(),
        current=0,
        total=frames,
        params=params,
        job_dir=job_dir,
        input_path=input_path,
        frames_dir=frames_dir,
        video_path=video_path,
    )

    queued = sum(1 for j in JOBS.jobs.values() if j.status == "QUEUED")
    running = sum(1 for j in JOBS.jobs.values() if j.status == "RUNNING")
    if queued >= MAX_QUEUE and running >= 1:
        raise RuntimeError("Too many jobs queued. Please try again in a bit.")

    JOBS.put(job)

    try:
        with open(os.path.join(job_dir, "meta.json"), "w", encoding="utf-8") as f:
            json.dump({**asdict(job), "params": params}, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

    return job

def get_job(job_id: str) -> Optional[Job]:
    return JOBS.get(job_id)

def model_loaded() -> bool:
    return ModelManager._loaded