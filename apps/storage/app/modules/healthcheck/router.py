from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

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
