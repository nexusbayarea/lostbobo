import os
from pathlib import Path

from pydantic_settings import BaseSettings

APP_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    SB_URL: str = os.getenv("SB_URL", "")
    SB_SECRET_KEY: str = os.getenv("SB_SECRET_KEY", "")
    SB_JWT_SECRET: str = os.getenv("SB_JWT_SECRET", "")

    S3_ACCESS_KEY: str = os.getenv("RUNPOD_S3_KEY", "")
    S3_SECRET_KEY: str = os.getenv("RUNPOD_S3_SECRET", "")
    S3_ENDPOINT: str = os.getenv("RUNPOD_S3_ENDPOINT", "")
    S3_REGION: str = os.getenv("RUNPOD_REGION", "us-east-1")
    S3_VOLUME_ID: str = os.getenv("RUNPOD_VOLUME_ID", "")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    QUEUE_HIGH: str = "simhpc:queue:high"
    QUEUE_MED: str = "simhpc:queue:medium"
    QUEUE_DEFAULT: str = "simhpc:queue:default"
    MIN_WARM_WORKERS: int = int(os.getenv("MIN_WARM_WORKERS", "1"))

    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "SimHPC"


settings = Settings()


def get_settings() -> Settings:
    return settings
