from typing import Self

from app.exceptions import ModelAlreadyExistsException, ModelNotFoundException
from app.modules.auth.exceptions import WrongCredentialsException
from app.modules.auth.schemas import LoginSchema, RegisterSchema, Sessionchema
from app.modules.auth.services.hash import HashService
from app.modules.auth.services.token import TokenService
from app.modules.operator.service import (
    OperatorCreateSchema,
    OperatorReadSchema,
    OperatorService,
)


class AuthService:
    def __init__(
        self: Self,
        hash_service: HashService,
        token_service: TokenService,
        operator_service: OperatorService,
    ) -> None:
        self.hash_service = hash_service
        self.token_service = token_service
        self.operator_service = operator_service

    async def login(self: Self, login_schema: LoginSchema) -> Sessionchema:
        try:
            operator = await self.operator_service.get_by_username(
                login_schema.username
            )
        except ModelNotFoundException as exc:
            raise WrongCredentialsException() from exc

        is_valid_password = self.hash_service.verify(
            login_schema.password, operator.password_hash
        )
        if not is_valid_password:
            raise WrongCredentialsException()

        access_token, refresh_token = self.token_service.create_pair(operator.id)
        return Sessionchema(access_token=access_token, refresh_token=refresh_token)

    async def register(
        self: Self, register_schema: RegisterSchema
    ) -> OperatorReadSchema:
        if await self.operator_service.exists_with_username(register_schema.username):
            raise ModelAlreadyExistsException()

        password_hash = self.hash_service.hash(register_schema.password)
        return await self.operator_service.create(
            OperatorCreateSchema(
                **register_schema.model_dump(), password_hash=password_hash
            )
        )

    async def verify(self: Self, access_token: str) -> OperatorReadSchema:
        payload = self.token_service.verify(access_token)
        return await self.operator_service.get(int(payload.sub))

    async def refresh(self: Self, refresh_token: str) -> str:
        payload = self.token_service.verify(refresh_token)
        access_token = self.token_service.create_access(int(payload.sub))
        return access_token

    async def get_subscription_token(self: Self, operator: OperatorReadSchema) -> str:
        token = self.token_service.create_subscription(operator.id)
        return token
