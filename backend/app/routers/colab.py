import httpx
import logging
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.core.config import settings


logger = logging.getLogger("app.routers.colab")
router = APIRouter(prefix="/colab", tags=["colab"])

@router.get("/ping")
async def colab_ping():
    if not settings.COLAB_API_BASE:
        raise HTTPException(status_code=500, detail="COLAB_API_BASE not configured")
    
    url = f"{settings.COLAB_API_BASE}/ping"
    headers = {"x-api-key": settings.COLAB_SHARED_SECRET} if settings.COLAB_SHARED_SECRET else {}

    try:
        async with httpx.AsyncClient(timeout = 60) as Client:
            response = await Client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error("Error pinging Colab API: %s", str(e))
        raise HTTPException(status_code=502, detail="Error pinging Colab API") from e


@router.post("/sky")
async def colab_sky(
    file: UploadFile = File(...),
    duration_s: float = Form(4.0),
    fps: int = Form(24),
):
    if not settings.COLAB_API_BASE:
        raise HTTPException(status_code=500, detail="COLAB_API_BASE not configured")
        
    url = f"{settings.COLAB_API_BASE}/sky"
    headers = {"x-api-key": settings.COLAB_SHARED_SECRET} if settings.COLAB_SHARED_SECRET else {}

    try:
        file_bytes = await file.read()
        files = {
            "file": (file.filename or "upload.jpg", file_bytes, file.content_type or "application/octet-stream")
        }

        data = {
            "duration_s": str(duration_s),
            "fps": str(fps),
        }


        async with httpx.AsyncClient(timeout = 300) as Client:
            response = await Client.post(url, headers=headers, files=files, data=data)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        text = e.response.text
        logger.error("Colab API returned error: %s", text)
        raise HTTPException(status_code=e.response.status_code, detail=text)
    except Exception as e:
        logger.error("Error calling Colab API: %s", str(e))
        raise HTTPException(status_code=502, detail="Error calling Colab API") from e
    

@router.post("/svd")
async def colab_svd(
    file: UploadFile = File(...),
    num_frames: int = Form(16),
    fps: int = Form(24),
    motion_bucket_id: int = Form(112),
    max_side: int = Form(640),
    seed: int = Form(42)
):
    if not settings.COLAB_API_BASE:
        raise HTTPException(status_code=500, detail="COLAB_API_BASE not configured")
    
    url = f"{settings.COLAB_API_BASE}/svd"
    headers = {"x-api-key": settings.COLAB_SHARED_SECRET} if settings.COLAB_SHARED_SECRET else {}

    file_bytes = await file.read()
    files = {"file": (file.filename or "image.png", file_bytes, file.content_type or "application/octet-stream")}
    data = {
        "num_frames": str(num_frames),
        "fps": str(fps),
        "motion_bucket_id": str(motion_bucket_id),
        "max_side": str(max_side),
        "seed": str(seed)
    }

    try:
        async with httpx.AsyncClient(timeout = 500) as Client:
            response = await Client.post(url, headers=headers, files=files, data=data)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:

        text = e.response.text
        logger.error("Colab API returned error: %s", text)
        raise HTTPException(status_code=e.response.status_code, detail=text)
    
    except Exception as e:
        logger.error("Error calling Colab API: %s", str(e))
        raise HTTPException(status_code=502, detail="Error calling Colab API") from e
    
@router.post("/svd/start")
async def svd_start_proxy(
    file: UploadFile = File(...),
    num_frames: int = Form(16),
    fps: int = Form(24),
    motion_bucket_id: int = Form(112),
    max_side: int = Form(640),
    seed: int = Form(42)
): 
    
    if not settings.COLAB_API_BASE:
        raise HTTPException(status_code=500, detail="COLAB_API_BASE not configured")
    
    file_bytes = await file.read()
    files = {"file": (file.filename or "image.png", file_bytes, file.content_type or "application/octet-stream")}
    data = {
        "num_frames": str(num_frames),
        "fps": str(fps),
        "motion_bucket_id": str(motion_bucket_id),
        "max_side": str(max_side),
        "seed": str(seed)
    }

    url = f"{settings.COLAB_API_BASE}/svd/start"
    headers = {"x-api-key": settings.COLAB_SHARED_SECRET} if settings.COLAB_SHARED_SECRET else {}

    try:
        async with httpx.AsyncClient(timeout = 500) as Client:
            response = await Client.post(url, headers=headers, files=files, data=data)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:

        text = e.response.text
        logger.error("Colab API returned error: %s", text)
        raise HTTPException(status_code=e.response.status_code, detail=text)
    
    except Exception as e:
        logger.error("Error calling Colab API: %s", str(e))
        raise HTTPException(status_code=502, detail="Error calling Colab API") from e
    
@router.get("/svd/status/{job_id}")
async def svd_status_proxy(job_id: str):
    
    if not settings.COLAB_API_BASE:
        raise HTTPException(status_code=500, detail="COLAB_API_BASE not configured")
    
    url = f"{settings.COLAB_API_BASE}/svd/status/{job_id}"
    headers = {"x-api-key": settings.COLAB_SHARED_SECRET} if settings.COLAB_SHARED_SECRET else {}
    try:
        async with httpx.AsyncClient(timeout = 500) as Client:
            response = await Client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        text = e.response.text
        logger.error("Colab API returned error: %s", text)
        raise HTTPException(status_code=e.response.status_code, detail=text)
    except Exception as e:
        logger.error("Error calling Colab API: %s", str(e))
        raise HTTPException(status_code=502, detail="Error calling Colab API") from e



@router.get("/svd/result/{job_id}")
async def svd_result_proxy(job_id: str):
    
    if not settings.COLAB_API_BASE:
        raise HTTPException(status_code=500, detail="COLAB_API_BASE not configured")
    url = f"{settings.COLAB_API_BASE}/svd/result/{job_id}"
    headers = {"x-api-key": settings.COLAB_SHARED_SECRET} if settings.COLAB_SHARED_SECRET else {}

    try:
        async with httpx.AsyncClient(timeout = 500) as Client:
            response = await Client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        text = e.response.text
        logger.error("Colab API returned error: %s", text)
        raise HTTPException(status_code=e.response.status_code, detail=text)
    except Exception as e:
        logger.error("Error calling Colab API: %s", str(e))
        raise HTTPException(status_code=502, detail="Error calling Colab API") from e