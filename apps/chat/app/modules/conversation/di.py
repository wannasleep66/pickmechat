from typing import Self
from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.conversation.repository import ConversationRepository
from app.modules.conversation.service import ConversationService


class ModuleProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def conversation_repository(
        self: Self, session: AsyncSession
    ) -> ConversationRepository:
        return ConversationRepository(session=session)

    @provide(scope=Scope.REQUEST)
    async def conversation_service(
        self: Self, conversation_repository: ConversationRepository
    ) -> ConversationService:
        return ConversationService(conversation_repository=conversation_repository)
