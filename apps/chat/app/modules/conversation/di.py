from typing import Self

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.conversation.repositories.conversation import ConversationRepository
from app.modules.conversation.repositories.last_read import LastReadRepository
from app.modules.conversation.service import ConversationService


class ModuleProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def conversation_repository(
        self: Self, session: AsyncSession
    ) -> ConversationRepository:
        return ConversationRepository(session=session)

    @provide(scope=Scope.REQUEST)
    async def last_read_repository(
        self: Self, session: AsyncSession
    ) -> LastReadRepository:
        return LastReadRepository(session=session)

    @provide(scope=Scope.REQUEST)
    async def conversation_service(
        self: Self,
        conversation_repository: ConversationRepository,
        last_read_repository: LastReadRepository,
    ) -> ConversationService:
        return ConversationService(
            conversation_repository=conversation_repository,
            last_read_repository=last_read_repository,
        )
