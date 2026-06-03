from typing import Self

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.strategy_options import joinedload

from app.modules.operator.models.operator import Operator
from app.modules.operator.schemas.operator import (
    OperatorCreateSchema,
    OperatorDetailsOutSchema,
    OperatorOutSchema,
    OperatorReadSchema,
    OperatorUpdateSchema,
)
from app.modules.rbac.models.operator_role import OperatorRole
from app.modules.rbac.models.role import Role
from app.modules.rbac.models.role_permission import RolePermission
from app.repositories.database import DatabaseRepository


class OperatorRepository(
    DatabaseRepository[
        Operator,
        OperatorCreateSchema,
        OperatorReadSchema,
        OperatorUpdateSchema,
    ]
):
    model_type = Operator
    model_schema = OperatorReadSchema

    async def get(
        self: Self, id_: int, with_deleted: bool = False
    ) -> OperatorOutSchema | None:
        stmt = (
            select(Operator)
            .options(
                joinedload(Operator.status),
                selectinload(Operator.roles_refs)
                .joinedload(OperatorRole.role)
                .selectinload(Role.permissions_refs)
                .joinedload(RolePermission.permission),
            )
            .filter_by(id=id_)
        )

        if not with_deleted:
            pass

        instance = await self.session.scalar(stmt)
        return OperatorOutSchema.model_validate(instance) if instance else None

    async def get_details(
        self: Self, operator_id: int
    ) -> OperatorDetailsOutSchema | None:
        stmt = (
            select(Operator)
            .options(
                joinedload(Operator.status),
                selectinload(Operator.assigments),
                selectinload(Operator.roles_refs)
                .joinedload(OperatorRole.role)
                .selectinload(Role.permissions_refs)
                .joinedload(RolePermission.permission),
            )
            .filter_by(id=operator_id)
        )
        instance = await self.session.scalar(stmt)
        return OperatorDetailsOutSchema.model_validate(instance) if instance else None

    async def get_all_detailed(
        self: Self, search: str | None = None
    ) -> list[OperatorDetailsOutSchema]:
        stmt = select(Operator).options(
            joinedload(Operator.status),
            selectinload(Operator.assigments),
            selectinload(Operator.roles_refs)
            .joinedload(OperatorRole.role)
            .selectinload(Role.permissions_refs)
            .joinedload(RolePermission.permission),
        )

        if search:
            stmt = stmt.filter(Operator.name.ilike(f"%{search}%"))

        instances = await self.session.scalars(stmt)
        return [OperatorDetailsOutSchema.model_validate(inst) for inst in instances]
