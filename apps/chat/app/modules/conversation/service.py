from datetime import datetime
from typing import Self

from app.exceptions import ModelNotFoundException
from app.modules.conversation.repository import (
    ConversationRepository,
)
from app.modules.conversation.schemas import (
    ConversationCreateSchema,
    ConversationDetailsOutSchema,
    ConversationOutSchema,
    ConversationQueryFilter,
    ConversationReadSchema,
    ConversationUpdateSchema,
)


class ConversationService:
    def __init__(self: Self, conversation_repository: ConversationRepository) -> None:
        self.conversation_repository = conversation_repository

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
        closed_conversation = await self.conversation_repository.update(
            conversation_to_close.id, ConversationUpdateSchema(closed_at=datetime.now())
        )
        return closed_conversation

    async def get(self: Self, conversation_id: int) -> ConversationReadSchema:
        conversation = await self.conversation_repository.get(conversation_id)
        if not conversation:
            raise ModelNotFoundException()

        return conversation

    async def get_details(
        self: Self, conversation_id: int
    ) -> ConversationDetailsOutSchema:
        conversation_details = await self.conversation_repository.get_details(
            conversation_id
        )
        if not conversation_details:
            raise ModelNotFoundException()

        return conversation_details

    async def get_all(
        self: Self,
        operator_id: int,
        filter: ConversationQueryFilter = "all",
    ) -> list[ConversationOutSchema]:
        return await self.conversation_repository.get_all_with_last_message(
            operator_id, filter
        )
