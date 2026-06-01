from typing import Any, Callable, Self

from sqlalchemy import Select, and_, desc, func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.functions import coalesce, count

from app.modules.assigment.model import Assigment
from app.modules.conversation.models.conversation import Conversation
from app.modules.conversation.models.last_read import LastRead
from app.modules.conversation.schemas.conversation import (
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
        self: Self, operator_id: int, conversation_id: int
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

        last_read_stmt = select(LastRead).filter_by(
            conversation_id=conversation.id, operator_id=operator_id
        )
        last_read = await self.session.scalar(last_read_stmt)

        unread_count_stmt = select(count(Message.id)).filter(
            Message.conversation_id == conversation.id,
            Message.id > coalesce(last_read.message_id if last_read else None, 0),
        )
        unread_count = await self.session.scalar(unread_count_stmt)

        return ConversationDetailsOutSchema.model_validate(
            {
                "conversation": conversation,
                "last_message": last_message,
                "last_read": last_read,
                "unread_count": unread_count if unread_count else 0,
            }
        )

    async def get_all_detailed(
        self: Self, operator_id: int, filter: ConversationQueryFilter = "all"
    ) -> list[ConversationOutSchema]:
        last_message_subquery = (
            select(Message.conversation_id, func.max(Message.id).label("max_id"))
            .group_by(Message.conversation_id)
            .subquery()
        )

        unread_count_subquery = (
            select(count(Message.id))
            .filter(
                Message.conversation_id == Conversation.id,
                Message.id > coalesce(LastRead.message_id, 0),
            )
            .correlate(Conversation, LastRead)
            .scalar_subquery()
        )

        apply_filter: Callable[[Select[Any]], Select[Any]] = {
            "assigned": lambda stmt: stmt.join(
                Assigment, Assigment.conversation_id == Conversation.id
            ).filter(Assigment.operator_id == operator_id),
            "closed": lambda stmt: stmt.filter(Conversation.closed_at.is_not(None)),
            "open": lambda stmt: stmt.filter(Conversation.closed_at.is_(None)),
            "all": lambda stmt: stmt,
        }[filter]

        stmt = (
            select(
                Conversation,
                Message,
                LastRead,
                unread_count_subquery.label("UnreadCount"),
            )
            .outerjoin(
                LastRead,
                (
                    and_(
                        LastRead.conversation_id == Conversation.id,
                        LastRead.operator_id == operator_id,
                    )
                ),
            )
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

        return [
            ConversationOutSchema.model_validate(
                {
                    "conversation": mapping.Conversation,
                    "last_message": mapping.Message,
                    "last_read": mapping.LastRead,
                    "unread_count": mapping.UnreadCount,
                }
            )
            for mapping in records.mappings().all()
        ]
