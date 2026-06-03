from typing import Self, cast

from sqlalchemy import delete, insert, select
from sqlalchemy.orm.strategy_options import selectinload

from app.modules.rbac.models.operator_role import OperatorRole
from app.modules.rbac.models.role import Role
from app.modules.rbac.models.role_permission import RolePermission
from app.modules.rbac.schemas import (
    RoleCreateSchema,
    RoleOutSchema,
    RoleReadSchema,
    RoleUpdateSchema,
)
from app.repositories.database import DatabaseRepository


class RoleRepository(
    DatabaseRepository[Role, RoleCreateSchema, RoleReadSchema, RoleUpdateSchema]
):
    model_type = Role
    model_schema = RoleReadSchema

    async def get(
        self: Self, id_: int, with_deleted: bool = False
    ) -> RoleOutSchema | None:
        stmt = (
            select(Role)
            .options(
                selectinload(Role.permissions_refs).joinedload(
                    RolePermission.permission
                )
            )
            .filter_by(id=id_)
        )

        if not with_deleted:
            pass

        instance = await self.session.scalar(stmt)
        return RoleOutSchema.model_validate(instance) if instance else None

    async def get_detailed(self: Self) -> list[RoleOutSchema]:
        stmt = select(Role).options(
            selectinload(Role.permissions_refs).joinedload(RolePermission.permission)
        )
        instances = await self.session.scalars(stmt)
        return [RoleOutSchema.model_validate(inst) for inst in instances]

    async def attach_to_operator(
        self: Self, role_id: int, operator_id: int
    ) -> RoleOutSchema:
        stmt = insert(OperatorRole).values(role_id=role_id, operator_id=operator_id)
        await self.session.execute(stmt)
        return cast(RoleOutSchema, await self.get(role_id))

    async def detach_from_operator(
        self: Self, role_id: int, operator_id: int
    ) -> RoleOutSchema:
        stmt = delete(OperatorRole).filter_by(role_id=role_id, operator_id=operator_id)
        await self.session.execute(stmt)
        return cast(RoleOutSchema, await self.get(role_id))

    async def exists_with_role_and_operator(
        self: Self, role_id: int, operator_id: int
    ) -> bool:
        stmt = select(OperatorRole).filter_by(role_id=role_id, operator_id=operator_id)
        instance = await self.session.scalar(stmt)
        return instance is not None
