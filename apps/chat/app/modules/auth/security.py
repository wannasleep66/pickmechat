from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.modules.auth.services.auth import AuthService
from app.modules.operator.schemas import OperatorReadSchema

oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login", refreshUrl="/auth/refresh")

OAuthToken = Annotated[str, Depends(oauth2)]


@inject
async def get_current_operator(
    token: OAuthToken, auth_service: FromDishka[AuthService]
) -> OperatorReadSchema:
    return await auth_service.verify(token)


OperatorDep = Annotated[OperatorReadSchema, Depends(get_current_operator)]
