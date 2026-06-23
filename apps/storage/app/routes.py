from fastapi import APIRouter, FastAPI

from app.modules.file.router import router as file_router
from app.modules.healthcheck.router import router as health_check_router


def use_routes(app: FastAPI) -> None:
    router = APIRouter()
    router.include_router(health_check_router)
    router.include_router(file_router)
    app.include_router(router=router)
