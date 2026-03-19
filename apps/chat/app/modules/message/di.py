from typing import Self

from dishka import Provider, Scope, provide
from faststream.rabbit import RabbitBroker
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.assigment.service import AssigmentService
from app.modules.conversation.service import ConversationService
from app.modules.message.repository import (
    MessageRepository,
)
from app.modules.message.service import (
    MessageService,
)
from app.modules.realtime.transport import RealtimeTransport


class ModuleProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def message_repository(self: Self, session: AsyncSession) -> MessageRepository:
        return MessageRepository(session=session)

    @provide(scope=Scope.REQUEST)
    def message_service(
        self: Self,
        assigment_service: AssigmentService,
        conversation_service: ConversationService,
        realtime_transport: RealtimeTransport,
        message_repository: MessageRepository,
        broker: RabbitBroker,
    ) -> MessageService:
        return MessageService(
            assigment_service=assigment_service,
            conversation_service=conversation_service,
            realtime_transport=realtime_transport,
            message_repository=message_repository,
            broker=broker,
        )
