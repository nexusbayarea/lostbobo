from fastapi import APIRouter
from backend.app.api.admin.observability import router as observability_router
from backend.app.api.endpoints.simulations import router as simulations_router

api_router = APIRouter()

api_router.include_router(observability_router, tags=["admin"])
api_router.include_router(simulations_router, prefix="/alpha", tags=["Simulations"])
