from pathlib import Path
from pydantic_settings import BaseSettings
import os

APP_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    SB_URL: str = os.getenv("SB_URL", "")
    SB_SECRET_KEY: str = os.getenv("SB_SECRET_KEY", "")
    SB_JWT_SECRET: str = os.getenv("SB_JWT_SECRET", "")
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "SimHPC"


settings = Settings()
