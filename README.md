# 🏛️ Archi-Video

Turn architectural renderings into short, cinematic videos with subtle motion.
The goal is to help architects present static renders more dynamically while staying faithful to the original images using Gen AI (diffusion models).
---

## 🚀 Features (so far)

- **FastAPI backend** (Dockerized).
- Endpoints:
  - `/health` → check service status.
  - `/video/static` → repeats a still image into a video.
  - `/video/light` → pulsing brightness/light effect.
  - `/video/sky` → animated procedural sky effect (mask sky + overlay moving texture).
  - `/colab/svd/start` → start a video generation job on Colab.
  - `/colab/svd/status/{job_id}` → poll job state (queued, running, done, error).
  - `/colab/svd/result/{job_id}` → fetch Drive links + metadata once complete.
- Outputs `.mp4` uploaded to google drive
- Responses return **shareable Drive Links**

---

## 🛠️ Tech Stack

- **Python 3.12**  
- **FastAPI + Uvicorn**  
- **NumPy / Pillow** (image processing)  
- **imageio-ffmpeg** (video encoding)  
- **Stable Video Diffusion (SVD)** on **Colab (T4 GPU)**
- **Docker + docker-compose**  
- **Cloudflared** tunnel to expose Colab server

---

## 📦 Setup

### Clone repo
```bash
git clone https://github.com/hn05012/archi-video.git
cd archi-video
```

### Run with Docker
```bash
docker-compose up --build
```
Service will be live at: http://127.0.0.1:8000


### 📍 Next Steps
- Optimize performance (downscale inputs, streaming encoding).
- Add a React frontend for uploads + preview.
- Explore GenAI-driven effects with Control nets
