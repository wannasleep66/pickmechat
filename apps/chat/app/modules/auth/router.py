from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Form, Response, status

from app.modules.auth.schemas import (
    LoginRequestSchema,
    LoginSchema,
    RegisterRequestSchema,
    RegisterSchema,
    SessionResponseSchema,
    SubscriptionResponseSchema,
)
from app.modules.auth.security import OAuthToken, OperatorDep
from app.modules.auth.services.auth import AuthService
from app.modules.operator.schemas import OperatorResponseSchema

router = APIRouter(prefix="/auth")


@router.post("/login")
@inject
async def login(
    response: Response,
    credentials: Annotated[LoginRequestSchema, Form()],
    auth_service: FromDishka[AuthService],
) -> SessionResponseSchema:
    """Авторизация пользователя"""

    session = await auth_service.login(LoginSchema(**credentials.model_dump()))
    response.set_cookie(
        key="session",
        value=session.refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
    )
    return SessionResponseSchema(access_token=session.access_token)


@router.post("/register", status_code=status.HTTP_201_CREATED)
@inject
async def register(
    credentials: RegisterRequestSchema,
    auth_service: FromDishka[AuthService],
) -> OperatorResponseSchema:
    """Создание пользователя"""

    operator = await auth_service.register(RegisterSchema(**credentials.model_dump()))
    return OperatorResponseSchema(**operator.model_dump())


@router.post("/subscription")
@inject
async def get_subscription_token(
    operator: OperatorDep, auth_service: FromDishka[AuthService]
) -> SubscriptionResponseSchema:
    """Получение сессии для авторизации в centrifugo"""

    subscription_token = await auth_service.get_subscription_token(operator)
    return SubscriptionResponseSchema(token=subscription_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def logout(
    response: Response,
) -> None:
    """Выход пользователя"""

    response.delete_cookie(key="session")


@router.post("/refresh")
@inject
async def refresh(
    token: OAuthToken,
    auth_service: FromDishka[AuthService],
) -> SessionResponseSchema:
    """Обновление сессии"""

    access_token = await auth_service.refresh(token)
    return SessionResponseSchema(access_token=access_token)


@router.get("/me")
async def get_current_operator(operator: OperatorDep) -> OperatorResponseSchema:
    """Получение текущего пользователя"""

    return OperatorResponseSchema(**operator.model_dump())
