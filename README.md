# 🏛️ Archi-Video

Turn architectural stills into short, cinematic videos with **subtle motion**—while staying faithful to the original render.

This proof-of-concept now runs **entirely on CPU** with a clean FastAPI backend and a minimal job API focused on a single, useful edit first: _“move the clouds, keep the building static”_ (prompt-only control).

---

## ✨ What’s here

- **FastAPI backend** (local, CPU-only)
- **AnimateDiff (SD 1.5) + AnimateLCM LoRA** for few-step CPU inference
- **Simple job flow**
  - `POST /svd/` → start image→video job
  - `GET  /svd/status/{id}` → poll progress (denoise steps + ETA)
  - `GET  /svd/result/{id}` → fetch final MP4 path
- **Single worker queue**, per-job folders, JSON metadata
- Static serving for results at `/backend/app/data/outputs/jobs{job_id}/out.mp4`

---

## 🧠 Model & strategy

- **Base**: `runwayml/stable-diffusion-v1-5`
- **Motion**: `guoyww/animatediff-motion-adapter-v1-5`
- **Few-step acceleration**: `LCMScheduler` + **AnimateLCM I2V LoRA** (`wangfuyun/AnimateLCM-I2V`)
- **CPU hygiene**: attention/vae slicing & tiling, channels-last, thread caps

---

## 📦 Setup (Local, CPU)

```bash
git clone https://github.com/hn05012/archi-video.git
cd archi-video

# (recommended) Python 3.12 virtualenv
python -m venv backend/.venv
# Windows
backend\.venv\Scripts\activate
# macOS/Linux
source backend/.venv/bin/activate

cd backend
pip install -r requirements.txt
```

## Start the server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## ⚠️ Limitations (current POC)

- **CPU-only**: Expect roughly **7–10 minutes** per short clip depending on resolution & params.
- **Prompt-only control** (no masks yet): reflective facades may show slight “breathing” when the sky changes.
- **Short clips**: optimized for ~6–10 frames @ 8–10 fps (quick loops).

## ☁️ Legacy: Colab/GPU workflow (archived/optional)

Before the CPU-only pivot, the POC could launch jobs on Google Colab (T4 GPU) and return Drive links:

- Endpoints (legacy):
  - `/colab/svd/start` → start a Colab job
  - `/colab/svd/status/{job_id}` → poll (queued, running, done, error)
  - `/colab/svd/result/{job_id}` → fetch Google Drive links + metadata

**High-level setup (legacy)**:

1. Open the Colab notebook (GPU runtime), install deps, run the FastAPI worker.
2. Expose the Colab server via **Cloudflared** tunnel to get a public URL.
3. Call the **/colab/svd/\*** endpoints from your local app; results were uploaded to Google Drive and the API returned shareable links.

⚠️ Note: I had to switch from Colab to local setup because of free tier limits on Colab
