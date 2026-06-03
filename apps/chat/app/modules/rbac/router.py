from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Path
from starlette import status

from app.modules.rbac.schemas import RoleResponseSchema
from app.modules.rbac.security import can
from app.modules.rbac.service import RBACService

router = APIRouter()


@router.get("/roles", dependencies=[can("roles:list")])
@inject
async def get_roles(rbac_service: FromDishka[RBACService]) -> list[RoleResponseSchema]:
    """
    Получение списка ролей
    """

    roles = await rbac_service.get_all()
    return [RoleResponseSchema(**role.model_dump()) for role in roles]


@router.get("/roles/{role_id}", dependencies=[can("roles:read")])
@inject
async def get_role(
    role_id: Annotated[int, Path(description="Идентификатор роли")],
    rbac_service: FromDishka[RBACService],
) -> RoleResponseSchema:
    """
    Получение роли по идентификатору
    """

    role = await rbac_service.get(role_id)
    return RoleResponseSchema(**role.model_dump())


@router.post(
    "/operators/{operator_id}/roles/{role_id}",
    dependencies=[can("roles:attach")],
)
@inject
async def attach_role_to_operator(
    operator_id: Annotated[int, Path(description="Идентификатор оператора")],
    role_id: Annotated[int, Path(description="Идентификатор роли")],
    rbac_service: FromDishka[RBACService],
) -> RoleResponseSchema:
    """
    Добавить роль пользователю
    """

    role = await rbac_service.attach_role(operator_id, role_id)
    return RoleResponseSchema(**role.model_dump())


@router.delete(
    "/operators/{operator_id}/roles/{role_id}",
    dependencies=[can("roles:detach")],
    status_code=status.HTTP_204_NO_CONTENT,
)
@inject
async def detach_role_from_operator(
    operator_id: Annotated[int, Path(description="Идентификатор оператора")],
    role_id: Annotated[int, Path(description="Идентификатор роли")],
    rbac_service: FromDishka[RBACService],
) -> None:
    """
    Убрать роль у пользователю
    """

    await rbac_service.detach_role(operator_id, role_id)
