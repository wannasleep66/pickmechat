from typing import Self

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.strategy_options import joinedload

from app.modules.operator.models.operator import Operator
from app.modules.operator.schemas.operator import (
    OperatorCreateSchema,
    OperatorDetailsOutSchema,
    OperatorOutSchema,
    OperatorReadSchema,
    OperatorUpdateSchema,
)
from app.repositories.database import DatabaseRepository


class OperatorRepository(
    DatabaseRepository[
        Operator,
        OperatorCreateSchema,
        OperatorReadSchema,
        OperatorUpdateSchema,
    ]
):
    model_type = Operator
    model_schema = OperatorReadSchema

    async def get_by_id(self: Self, operator_id: int) -> OperatorOutSchema | None:
        stmt = (
            select(Operator)
            .options(joinedload(Operator.status))
            .filter_by(id=operator_id)
        )
        instance = await self.session.scalar(stmt)
        return OperatorOutSchema.model_validate(instance) if instance else None

    async def get_details(
        self: Self, operator_id: int
    ) -> OperatorDetailsOutSchema | None:
        stmt = (
            select(Operator)
            .options(joinedload(Operator.status), selectinload(Operator.assigments))
            .filter_by(id=operator_id)
        )
        instance = await self.session.scalar(stmt)
        return OperatorDetailsOutSchema.model_validate(instance) if instance else None

    async def get_all_detailed(self: Self) -> list[OperatorDetailsOutSchema]:
        stmt = select(Operator).options(
            joinedload(Operator.status), selectinload(Operator.assigments)
        )
        instances = await self.session.scalars(stmt)
        return [OperatorDetailsOutSchema.model_validate(inst) for inst in instances]
