from typing import Self

from sqlalchemy.dialects.postgresql import insert

from app.modules.operator.models.availability_status import AvailabilityStatus
from app.modules.operator.schemas.availability_status import (
    AvailabilityStatusCreateSchema,
    AvailabilityStatusReadSchema,
    AvailabilityStatusUpdateSchema,
)
from app.repositories.database import DatabaseRepository


class AvailabilityStatusRepository(
    DatabaseRepository[
        AvailabilityStatus,
        AvailabilityStatusCreateSchema,
        AvailabilityStatusReadSchema,
        AvailabilityStatusUpdateSchema,
    ]
):
    model_type = AvailabilityStatus
    model_schema = AvailabilityStatusReadSchema

    async def upsert_by_operator(
        self: Self, operator_id: int, update_data: AvailabilityStatusUpdateSchema
    ) -> AvailabilityStatusReadSchema:
        data = update_data.model_dump(exclude=None)
        stmt = (
            insert(AvailabilityStatus)
            .values(**data, operator_id=operator_id)
            .on_conflict_do_update(
                index_elements=[AvailabilityStatus.operator_id],
                set_=data,
            )
            .returning(AvailabilityStatus)
        )
        upserted = await self.session.scalar(stmt)
        return AvailabilityStatusReadSchema.model_validate(upserted)
