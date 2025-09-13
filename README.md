# 🏛️ Archi-Video

Turn **architectural renderings** into short, cinematic videos with subtle motion.  
The goal is to help architects present static renders more dynamically while staying faithful to the original images.  
Future versions will explore **Generative AI** (e.g., diffusion, ControlNets) for richer video effects.

---

## 🚀 Features (so far)

- **FastAPI backend** (Dockerized).
- Endpoints:
  - `/health` → check service status.
  - `/video/static` → repeats a still image into a video.
  - `/video/light` → pulsing brightness/light effect.
  - `/video/sky` → animated procedural sky effect (mask sky + overlay moving texture).
- Outputs `.mp4` 

---

## 🛠️ Tech Stack

- **Python 3.12**  
- **FastAPI + Uvicorn**  
- **NumPy / Pillow** (image processing)  
- **imageio-ffmpeg** (video encoding)  
- **Docker + docker-compose**  

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
Service will be live at: http://localhost:8000


### 📍 Next Steps
- Add /video/parallax using depth estimation models (MiDaS/ZoeDepth).
- Optimize performance (downscale inputs, streaming encoding).
- Add a React frontend for uploads + preview.
- Explore GenAI-driven effects (diffusion-based sky replacement, animated lighting, etc.).

