from fastapi import APIRouter
from app.api.routes.workspace import router as workspace_router
from app.api.routes.auto_research import router as auto_research_router

api_router = APIRouter()
api_router.include_router(workspace_router)
api_router.include_router(auto_research_router)
