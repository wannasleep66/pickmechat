from datetime import datetime
from typing import Self

from loguru import logger

from app.exceptions import ModelNotFoundException
from app.modules.conversation.repositories.conversation import (
    ConversationRepository,
)
from app.modules.conversation.repositories.last_read import LastReadRepository
from app.modules.conversation.schemas.conversation import (
    ConversationCreateSchema,
    ConversationDetailsOutSchema,
    ConversationOutSchema,
    ConversationQueryFilter,
    ConversationReadSchema,
    ConversationUpdateSchema,
)
from app.modules.conversation.schemas.last_read import (
    LastReadCreateSchema,
    LastReadInSchema,
    LastReadUpdateSchema,
)
from app.modules.operator.schemas.operator import OperatorOutSchema


class ConversationService:
    def __init__(
        self: Self,
        conversation_repository: ConversationRepository,
        last_read_repository: LastReadRepository,
    ) -> None:
        self.conversation_repository = conversation_repository
        self.last_read_repository = last_read_repository

    async def get_or_create(
        self: Self, conversation_create: ConversationCreateSchema
    ) -> ConversationReadSchema:
        conversation = await self.conversation_repository.get_by(
            external_user_id=conversation_create.external_user_id
        )
        if not conversation:
            conversation = await self.conversation_repository.create(
                conversation_create
            )
        return conversation

    async def close(self: Self, conversation_id: int) -> ConversationReadSchema:
        conversation_to_close = await self.get(conversation_id)
        closed_conversation = await self.conversation_repository.update_closed_at(
            conversation_to_close.id,
            closed_at=datetime.now() if not conversation_to_close.closed_at else None,
        )
        return closed_conversation

    async def set_last_read(
        self: Self, operator: OperatorOutSchema, last_read_in: LastReadInSchema
    ) -> None:

        last_read = await self.last_read_repository.get_by(
            operator_id=operator.id, conversation_id=last_read_in.conversation_id
        )

        if not last_read:
            await self.last_read_repository.create(
                LastReadCreateSchema(
                    operator_id=operator.id,
                    conversation_id=last_read_in.conversation_id,
                    message_id=last_read_in.message_id,
                )
            )
            return

        await self.last_read_repository.update(
            last_read.id, LastReadUpdateSchema(message_id=last_read_in.message_id)
        )

        logger.info(
            "Updated last read for operator {operator_id} in conversation {conversation_id} to message {message_id}",
            operator_id=last_read.operator_id,
            conversation_id=last_read_in.conversation_id,
            message_id=last_read_in.message_id,
        )

    async def get(self: Self, conversation_id: int) -> ConversationReadSchema:
        conversation = await self.conversation_repository.get(conversation_id)
        if not conversation:
            raise ModelNotFoundException()

        return conversation

    async def get_details(
        self: Self, operator: OperatorOutSchema, conversation_id: int
    ) -> ConversationDetailsOutSchema:
        conversation_details = await self.conversation_repository.get_details(
            operator.id, conversation_id
        )
        if not conversation_details:
            raise ModelNotFoundException()

        return conversation_details

    async def get_all(
        self: Self,
        operator: OperatorOutSchema,
        filter: ConversationQueryFilter = "all",
    ) -> list[ConversationOutSchema]:
        return await self.conversation_repository.get_all_detailed(operator.id, filter)
