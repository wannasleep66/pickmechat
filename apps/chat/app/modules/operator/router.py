from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Path

from app.modules.operator.schemas import OperatorResponseSchema
from app.modules.operator.service import OperatorService

router = APIRouter(prefix="/operators")


@router.get("/{operator_id}")
@inject
async def get_operator(
    operator_id: Annotated[int, Path(..., description="Идентификатор оператора")],
    operator_service: FromDishka[OperatorService],
) -> OperatorResponseSchema:
    operator = await operator_service.get(operator_id)
    return OperatorResponseSchema(**operator.model_dump())


@router.get("/")
@inject
async def get_all_operators(
    operator_service: FromDishka[OperatorService],
) -> list[OperatorResponseSchema]:
    operators = await operator_service.get_all()
    return [OperatorResponseSchema(**op.model_dump()) for op in operators]
