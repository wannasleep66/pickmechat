from typing import Self

from loguru import logger

from app.exceptions import ModelAlreadyExistsException, ModelNotFoundException
from app.modules.operator.service import OperatorService
from app.modules.rbac.repositories.role import RoleRepository
from app.modules.rbac.schemas import RoleOutSchema


class RBACService:
    def __init__(
        self: Self, role_repository: RoleRepository, operator_service: OperatorService
    ) -> None:
        self.role_repository = role_repository
        self.operator_service = operator_service

    async def attach_role(self: Self, operator_id: int, role_id: int) -> RoleOutSchema:
        if await self.has_role(operator_id, role_id):
            raise ModelAlreadyExistsException()

        operator_to_update = await self.operator_service.get(operator_id)
        role_to_attach = await self.get(role_id)
        attached_role = await self.role_repository.attach_to_operator(
            role_to_attach.id, operator_to_update.id
        )
        logger.info(
            "Attached role {role_id} to operator {operator_id}",
            role_id=attached_role.id,
            operator_id=operator_to_update.id,
        )
        return attached_role

    async def detach_role(self: Self, operator_id: int, role_id: int) -> None:
        if not await self.has_role(operator_id, role_id):
            raise ModelNotFoundException()

        operator_to_update = await self.operator_service.get(operator_id)
        role_to_detach = await self.get(role_id)
        await self.role_repository.detach_from_operator(
            role_to_detach.id, operator_to_update.id
        )
        logger.info(
            "Detached role {role_id} from operator {operator_id}",
            role_id=role_to_detach.id,
            operator_id=operator_to_update.id,
        )

    async def can(self: Self, operator_id: int, *required_permissions: str) -> bool:
        operator_to_check = await self.operator_service.get(operator_id)
        operator_permissions = [
            permission
            for role in operator_to_check.roles
            for permission in role.permissions
        ]
        return all(
            permission in operator_permissions for permission in required_permissions
        )

    async def has_role(self: Self, operator_id: int, role_id: int) -> bool:
        return await self.role_repository.exists_with_role_and_operator(
            role_id, operator_id
        )

    async def get(self: Self, role_id: int) -> RoleOutSchema:
        role = await self.role_repository.get(role_id)
        if not role:
            raise ModelNotFoundException()
        return role

    async def get_all(self: Self) -> list[RoleOutSchema]:
        return await self.role_repository.get_detailed()
