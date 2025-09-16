import httpx
import logging
from fastapi import APIRouter, HTTPException
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
