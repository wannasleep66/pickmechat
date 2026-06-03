from typing import Annotated, Any

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.modules.auth.services.auth import AuthService
from app.modules.operator.schemas.operator import OperatorOutSchema

oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login", refreshUrl="/auth/refresh")

OAuthToken = Annotated[str, Depends(oauth2)]


@inject
async def get_current_operator(
    token: OAuthToken, auth_service: FromDishka[AuthService]
) -> OperatorOutSchema:
    return await auth_service.verify(token)


def auth() -> Any:
    return Depends(get_current_operator)


OperatorDep = Annotated[OperatorOutSchema, Depends(get_current_operator)]
