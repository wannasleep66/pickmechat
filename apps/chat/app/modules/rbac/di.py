from typing import Self

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.operator.service import OperatorService
from app.modules.rbac.repositories.role import RoleRepository
from app.modules.rbac.service import RBACService


class ModuleProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def role_repository(self: Self, session: AsyncSession) -> RoleRepository:
        return RoleRepository(session=session)

    @provide(scope=Scope.REQUEST)
    def rbac_service(
        self: Self, role_repository: RoleRepository, operator_service: OperatorService
    ) -> RBACService:
        return RBACService(
            role_repository=role_repository, operator_service=operator_service
        )
