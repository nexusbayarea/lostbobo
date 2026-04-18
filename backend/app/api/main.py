from fastapi import APIRouter
from backend.app.api.admin.observability import router as observability_router

api_router = APIRouter()

api_router.include_router(observability_router, tags=["admin"])
