from typing import Self

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.modules.assigment.model import Assigment
from app.modules.assigment.schemas import (
    AssigmentCreateSchema,
    AssigmentReadSchema,
    AssigmentUpdateSchema,
)
from app.modules.conversation.schemas.conversation import ConversationAssigmentOutSchema
from app.modules.operator.models.operator import Operator
from app.modules.operator.schemas.operator import OperatorAssigmentOutSchema
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
    ) -> list[ConversationAssigmentOutSchema]:
        stmt = (
            select(Assigment)
            .options(joinedload(Assigment.operator).joinedload(Operator.status))
            .filter_by(conversation_id=conversation_id)
        )
        if not with_deleted:
            stmt = stmt.filter_by(deleted_at=None)
        instances = await self.session.scalars(stmt)
        return [
            ConversationAssigmentOutSchema.model_validate(inst) for inst in instances
        ]

    async def get_all_by_operator(
        self: Self, operator_id: int, with_deleted: bool = False
    ) -> list[OperatorAssigmentOutSchema]:
        stmt = select(Assigment).filter_by(operator_id=operator_id)
        if not with_deleted:
            stmt = stmt.filter_by(deleted_at=None)
        instances = await self.session.scalars(stmt)
        return [OperatorAssigmentOutSchema.model_validate(inst) for inst in instances]
