from typing import Self

from dishka import Provider, provide, Scope

from app.modules.auth.services.hash import HashService
from app.modules.auth.services.token import TokenService
from app.modules.auth.services.auth import AuthService
from app.modules.operator.service import OperatorService
from app.settings import AuthSettings


class ModuleProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def hash_service(self: Self) -> HashService:
        return HashService()

    @provide(scope=Scope.REQUEST)
    def token_service(self: Self, settings: AuthSettings) -> TokenService:
        return TokenService(settings=settings)

    @provide(scope=Scope.REQUEST)
    def auth_service(
        self: Self,
        hash_service: HashService,
        token_service: TokenService,
        operator_service: OperatorService,
    ) -> AuthService:
        return AuthService(
            hash_service=hash_service,
            token_service=token_service,
            operator_service=operator_service,
        )
