from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Path, Query

from app.modules.auth.security import OperatorDep, auth
from app.modules.operator.schemas.availability_status import (
    AvailabilityStatusResponseSchema,
)
from app.modules.operator.schemas.operator import (
    OperatorChangeAvailabilityRequestSchema,
    OperatorDetailsResponseSchema,
    OperatorUpdateRequestSchema,
)
from app.modules.operator.service import OperatorService

router = APIRouter(prefix="/operators")


@router.get("/{operator_id}", dependencies=[auth()])
@inject
async def get_operator(
    operator_id: Annotated[int, Path(..., description="Идентификатор оператора")],
    operator_service: FromDishka[OperatorService],
) -> OperatorDetailsResponseSchema:
    operator = await operator_service.get_details(operator_id)
    return OperatorDetailsResponseSchema(**operator.model_dump())


@router.get("/", dependencies=[auth()])
@inject
async def get_all_operators(
    operator_service: FromDishka[OperatorService],
    search: str | None = Query(None, description="Поиск по имени"),
) -> list[OperatorDetailsResponseSchema]:
    operators = await operator_service.get_all(search=search)
    return [OperatorDetailsResponseSchema(**op.model_dump()) for op in operators]


@router.put("/me/profile")
@inject
async def update_profile(
    operator: OperatorDep,
    operator_update: OperatorUpdateRequestSchema,
    operator_service: FromDishka[OperatorService],
) -> OperatorDetailsResponseSchema:
    updated_operator = await operator_service.update(operator, operator_update)
    return OperatorDetailsResponseSchema(**updated_operator.model_dump())


@router.put("/me/availability")
@inject
async def change_availability_status(
    operator: OperatorDep,
    operator_update: OperatorChangeAvailabilityRequestSchema,
    operator_service: FromDishka[OperatorService],
) -> AvailabilityStatusResponseSchema:
    status = await operator_service.change_availability(
        operator, operator_update.status
    )
    return AvailabilityStatusResponseSchema(**status.model_dump())
