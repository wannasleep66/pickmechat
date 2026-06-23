from sqlalchemy import desc, select

from app.modules.message.models.message import Message
from app.modules.message.schemas.message import (
    MessageCreateSchema,
    MessageOutSchema,
    MessageReadSchema,
    MessageUpdateSchema,
)
from app.repositories.database import DatabaseRepository
from app.schemas.pagination import CursorPaginationMeta, Paginated


class MessageRepository(
    DatabaseRepository[
        Message,
        MessageCreateSchema,
        MessageReadSchema,
        MessageUpdateSchema,
    ]
):
    model_type = Message
    model_schema = MessageReadSchema

    async def get_by_conversation(
        self,
        conversation_id: int,
        cursor: int | None = None,
        limit: int = 25,
    ) -> Paginated[list[MessageOutSchema]]:
        stmt = (
            select(Message)
            .filter_by(conversation_id=conversation_id)
            .order_by(desc(Message.id))
            .limit(limit + 1)
        )

        if cursor:
            stmt = stmt.filter(Message.id < cursor)

        instances = list(await self.session.scalars(stmt))
        has_more = len(instances) > limit
        data = instances[:limit][::-1]
        return Paginated(
            data=[MessageOutSchema.model_validate(item) for item in data],
            pagination=CursorPaginationMeta(
                next_cursor=data[0].id if has_more else None
            ),
        )
