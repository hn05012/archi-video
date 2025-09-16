
import logging
import time
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.logging_setup import RequestIDFilter, request_id_var
from app.routers.video import router as video_router


RequestIDFilter.setup_Logging("INFO")

logger = logging.getLogger("app.main")

app = FastAPI(title="Image to Video API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


app.include_router(video_router)
