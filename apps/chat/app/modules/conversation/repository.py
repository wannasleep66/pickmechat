from typing import Self

from sqlalchemy import desc, func, select
from sqlalchemy.orm import selectinload

from app.modules.assigment.model import Assigment
from app.modules.conversation.model import Conversation
from app.modules.conversation.schemas import (
    ConversationCreateSchema,
    ConversationDetailsOutSchema,
    ConversationOutSchema,
    ConversationQueryFilter,
    ConversationReadSchema,
    ConversationUpdateSchema,
)
from app.modules.message.model import Message
from app.repositories.database import DatabaseRepository


class ConversationRepository(
    DatabaseRepository[
        Conversation,
        ConversationCreateSchema,
        ConversationReadSchema,
        ConversationUpdateSchema,
    ]
):
    model_type = Conversation
    model_schema = ConversationReadSchema

    async def get_details(
        self: Self, conversation_id: int
    ) -> ConversationDetailsOutSchema | None:
        stmt = (
            select(Conversation)
            .options(
                selectinload(
                    Conversation.assigments.and_(Assigment.deleted_at.is_(None))
                ).joinedload(Assigment.operator)
            )
            .filter_by(id=conversation_id)
        )

        conversation = await self.session.scalar(stmt)
        if not conversation:
            return None

        last_message_stmt = (
            select(Message)
            .filter(Message.conversation_id == conversation.id)
            .order_by(desc(Message.id))
            .limit(1)
        )
        last_message = await self.session.scalar(last_message_stmt)
        return ConversationDetailsOutSchema.model_validate((conversation, last_message))

    async def get_all_with_last_message(
        self: Self, operator_id: int, filter: ConversationQueryFilter = "all"
    ) -> list[ConversationOutSchema]:
        last_message_subquery = (
            select(Message.conversation_id, func.max(Message.id).label("max_id"))
            .group_by(Message.conversation_id)
            .subquery()
        )

        apply_filter = {
            "assigned": lambda stmt: stmt.join(
                Assigment, Assigment.conversation_id == Conversation.id
            ).filter(Assigment.operator_id == operator_id),
            "closed": lambda stmt: stmt.filter(Conversation.closed_at.is_not(None)),
            "open": lambda stmt: stmt.filter(Conversation.closed_at.is_(None)),
            "all": lambda stmt: stmt,
        }[filter]

        stmt = (
            select(Conversation, Message)
            .outerjoin(
                last_message_subquery,
                Conversation.id == last_message_subquery.c.conversation_id,
            )
            .outerjoin(
                Message,
                (Message.conversation_id == last_message_subquery.c.conversation_id)
                & (Message.id == last_message_subquery.c.max_id),
            )
        )

        stmt = apply_filter(stmt)

        records = await self.session.execute(stmt)
        return [ConversationOutSchema.model_validate(r.tuple()) for r in records.all()]
