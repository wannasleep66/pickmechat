from typing import Self

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.assigment.repository import AssigmentRepository
from app.modules.assigment.service import AssigmentService
from app.modules.conversation.service import ConversationService
from app.modules.operator.service import OperatorService
from app.modules.realtime.transport import RealtimeTransport


class ModuleProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def assigment_repository(self: Self, session: AsyncSession) -> AssigmentRepository:
        return AssigmentRepository(session=session)

    @provide
    def assigment_service(
        self: Self,
        assigment_repository: AssigmentRepository,
        operator_service: OperatorService,
        conversation_service: ConversationService,
        realtime_transport: RealtimeTransport,
    ) -> AssigmentService:
        return AssigmentService(
            assigment_repository=assigment_repository,
            operator_service=operator_service,
            conversation_service=conversation_service,
            realtime_transport=realtime_transport,
        )
