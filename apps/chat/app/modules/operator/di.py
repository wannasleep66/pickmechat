from typing import Self

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.operator.repositories.availability_status import (
    AvailabilityStatusRepository,
)
from app.modules.operator.repositories.operator import OperatorRepository
from app.modules.operator.service import OperatorService
from app.modules.realtime.transport import RealtimeTransport


class ModuleProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def operator_repository(self: Self, session: AsyncSession) -> OperatorRepository:
        return OperatorRepository(session=session)

    @provide(scope=Scope.REQUEST)
    def status_repository(
        self: Self, session: AsyncSession
    ) -> AvailabilityStatusRepository:
        return AvailabilityStatusRepository(session=session)

    @provide(scope=Scope.REQUEST)
    def operator_service(
        self: Self,
        operator_repository: OperatorRepository,
        status_repository: AvailabilityStatusRepository,
        realtime_transport: RealtimeTransport,
    ) -> OperatorService:
        return OperatorService(
            operator_repository=operator_repository,
            status_repository=status_repository,
            realtime_transport=realtime_transport,
        )
