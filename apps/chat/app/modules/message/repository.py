from sqlalchemy import desc, select
from app.repositories.database import DatabaseRepository
from app.modules.message.model import Message
from app.modules.message.schemas import (
    MessageCreateSchema,
    MessageOutSchema,
    MessageReadSchema,
    MessageUpdateSchema,
)


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
        self, conversation_id: int, before_id: int | None = None, limit: int = 25
    ) -> list[MessageOutSchema]:
        stmt = (
            select(Message)
            .filter_by(conversation_id=conversation_id)
            .order_by(desc(Message.timestamp))
            .limit(limit)
        )

        if before_id:
            stmt = stmt.filter(Message.id < before_id)

        instances = await self.session.scalars(stmt)
        return [MessageOutSchema.model_validate(inst) for inst in instances]
