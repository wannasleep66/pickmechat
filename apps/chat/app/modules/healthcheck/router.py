from dishka.entities.depends_marker import FromDishka
from dishka.integrations.fastapi import inject
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from app.modules.healthcheck.schemas import HealthCheckResponseSchema

router = APIRouter()


@router.get("/")
@inject
async def health_check(session: FromDishka[AsyncSession]) -> HealthCheckResponseSchema:
    """
    Проверка работоспособности сервиса
    """

    await session.execute(text("SELECT VERSION()"))
    return HealthCheckResponseSchema(status="ok")
