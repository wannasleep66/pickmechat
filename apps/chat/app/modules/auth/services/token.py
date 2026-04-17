from datetime import datetime, timedelta
from typing import Any, Self

import jwt

from app.modules.auth.exceptions import InvalidTokenException
from app.modules.auth.schemas import TokenPayload
from app.settings import AuthSettings


class TokenService:
    def __init__(self: Self, *, settings: AuthSettings) -> None:
        self.settings = settings

    def create_pair(self: Self, sub: int) -> tuple[str, str]:
        access = self.create_access(sub)
        refresh = self.create_refresh(sub)
        return access, refresh

    def create_access(self: Self, sub: int) -> str:
        now = datetime.now()
        return self.encode(
            TokenPayload(
                sub=str(sub),
                exp=now + timedelta(minutes=self.settings.access_token_ttl),
            ).model_dump()
        )

    def create_refresh(self: Self, sub: int) -> str:
        now = datetime.now()
        return self.encode(
            TokenPayload(
                sub=str(sub),
                exp=now + timedelta(minutes=self.settings.refresh_token_ttl),
            ).model_dump()
        )

    def create_subscription(self: Self, sub: int) -> str:
        now = datetime.now()
        return self.encode(
            TokenPayload(
                sub=str(sub),
                exp=now + timedelta(minutes=self.settings.subscription_token_ttl),
            ).model_dump()
        )

    def verify(self: Self, token: str) -> TokenPayload:
        try:
            payload = self.decode(token)
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as exc:
            raise InvalidTokenException()
        return TokenPayload(**payload)

    def encode(self: Self, payload: dict[str, Any]) -> str:
        return jwt.encode(payload, self.settings.secret, self.settings.algorithm)

    def decode(self: Self, token: str) -> dict[str, Any]:
        return jwt.decode(
            token,
            self.settings.secret,
            algorithms=[self.settings.algorithm],
            options={"verify_exp": True, "verify_sub": False},
        )
