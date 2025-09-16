import os
from pydantic import BaseModel

class Settings(BaseModel):
    COLAB_API_BASE: str = os.getenv("COLAB_API_BASE", "").rstrip("/")
    COLAB_SHARED_SECRET: str = os.getenv("COLAB_SHARED_SECRET", "")

settings = Settings()