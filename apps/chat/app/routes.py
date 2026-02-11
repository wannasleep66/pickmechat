from fastapi import APIRouter, FastAPI

from app.modules.healthcheck.router import router as health_check_router


def use_routes(app: FastAPI) -> None:
    router = APIRouter()
    router.include_router(health_check_router)
    app.include_router(router=router)
