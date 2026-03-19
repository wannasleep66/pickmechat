from typing import Self

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.operator.repository import OperatorRepository
from app.modules.operator.service import OperatorService


class ModuleProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def operator_repository(self: Self, session: AsyncSession) -> OperatorRepository:
        return OperatorRepository(session=session)

    @provide(scope=Scope.REQUEST)
    def operator_service(
        self: Self, operator_repository: OperatorRepository
    ) -> OperatorService:
        return OperatorService(operator_repository=operator_repository)
