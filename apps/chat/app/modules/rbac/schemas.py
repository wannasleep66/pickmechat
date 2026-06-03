from typing import Any, Self

from pydantic.config import ExtraValues

from app.modules.rbac.models.role import Role
from app.schemas.crud import CreateSchema, ReadSchema, UpdateSchema
from app.schemas.request_response import ResponseSchema


class RoleReadSchema(ReadSchema):
    name: str
    description: str | None = None


class RoleCreateSchema(CreateSchema):
    name: str
    description: str | None = None


class RoleUpdateSchema(UpdateSchema):
    name: str | None = None
    description: str | None = None


class RoleOutSchema(RoleReadSchema):
    permissions: list[str]

    @classmethod
    def model_validate(
        cls: type[Self],
        obj: Role,
        *,
        strict: bool | None = None,
        extra: ExtraValues | None = None,
        from_attributes: bool | None = None,
        context: Any | None = None,
        by_alias: bool | None = None,
        by_name: bool | None = None,
    ) -> Self:
        return super().model_validate(
            cls(
                id=obj.id,
                name=obj.name,
                description=obj.description,
                permissions=[
                    f"{ref.permission.resource}:{ref.permission.action}"
                    for ref in obj.permissions_refs
                ],
            ).model_dump(),
            strict=strict,
            extra=extra,
            from_attributes=from_attributes,
            context=context,
            by_alias=by_alias,
            by_name=by_name,
        )


class RoleResponseSchema(RoleOutSchema, ResponseSchema): ...
