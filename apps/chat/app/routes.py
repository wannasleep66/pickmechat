from fastapi import APIRouter, FastAPI

from app.modules.assigment.router import router as assigment_router
from app.modules.auth.router import router as auth_router
from app.modules.conversation.router import router as conversation_router
from app.modules.healthcheck.router import router as health_check_router
from app.modules.message.router import router as message_router
from app.modules.operator.router import router as operator_router


def use_routes(app: FastAPI) -> None:
    router = APIRouter()
    router.include_router(health_check_router)
    router.include_router(operator_router, tags=["Операторы"])
    router.include_router(auth_router, tags=["Авторизация"])
    router.include_router(message_router, tags=["Диалоги"])
    router.include_router(conversation_router, tags=["Диалоги"])
    router.include_router(assigment_router, tags=["Диалоги"])
    app.include_router(router=router)
