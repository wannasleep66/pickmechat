from typing import Self

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.modules.assigment.model import Assigment
from app.modules.conversation.model import Conversation
from app.modules.conversation.schemas import (
    ConversationCreateSchema,
    ConversationDetailsOutSchema,
    ConversationOutSchema,
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
        instance = await self.session.scalar(stmt)
        return (
            ConversationDetailsOutSchema.model_validate(instance) if instance else None
        )

    async def get_all_with_last_message(self: Self) -> list[ConversationOutSchema]:
        last_message_stats = (
            select(Message.conversation_id, func.max(Message.id).label("max_id"))
            .group_by(Message.conversation_id)
            .subquery()
        )

        stmt = (
            select(Conversation, Message)
            .outerjoin(
                last_message_stats,
                Conversation.id == last_message_stats.c.conversation_id,
            )
            .outerjoin(
                Message,
                (Message.conversation_id == last_message_stats.c.conversation_id)
                & (Message.id == last_message_stats.c.max_id),
            )
        )

        records = await self.session.execute(stmt)
        return [ConversationOutSchema.model_validate(r.tuple()) for r in records.all()]
