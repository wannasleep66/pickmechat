from typing import Self

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.modules.assigment.model import Assigment
from app.modules.assigment.schemas import (
    AssigmentCreateSchema,
    AssigmentOutSchema,
    AssigmentReadSchema,
    AssigmentUpdateSchema,
)
from app.repositories.database import DatabaseRepository


class AssigmentRepository(
    DatabaseRepository[
        Assigment,
        AssigmentCreateSchema,
        AssigmentReadSchema,
        AssigmentUpdateSchema,
    ]
):
    model_type = Assigment
    model_schema = AssigmentReadSchema

    async def get_all_by_conversation(
        self: Self, conversation_id: int, with_deleted: bool = False
    ) -> list[AssigmentOutSchema]:
        stmt = (
            select(Assigment)
            .options(joinedload(Assigment.operator))
            .filter_by(conversation_id=conversation_id)
        )
        if not with_deleted:
            stmt = stmt.filter_by(deleted_at=None)
        instances = await self.session.scalars(stmt)
        return [AssigmentOutSchema.model_validate(inst) for inst in instances]
