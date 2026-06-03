from typing import Any

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends
from fastapi.exceptions import HTTPException
from starlette import status

from app.modules.auth.security import OperatorDep
from app.modules.rbac.service import RBACService
from app.schemas.exception import ApplicationExceptionSchema


def can(*required_permissions: str) -> Any:

    async def check_permissions(
        operator: OperatorDep, rbac_service: FromDishka[RBACService]
    ) -> None:
        has_permission = await rbac_service.can(operator.id, *required_permissions)
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=[
                    ApplicationExceptionSchema(
                        type="PermissionException",
                        msg="Недостаточно прав",
                    ).model_dump()
                ],
            )

    return Depends(inject(check_permissions))
