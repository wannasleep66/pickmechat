from datetime import datetime

from pydantic import BaseModel

from app.schemas.request_response import RequestSchema


class LoginSchema(BaseModel):
    username: str
    password: str


class RegisterSchema(BaseModel):
    username: str
    password: str
    name: str
    image_url: str | None = None


class TokenPayload(BaseModel):
    sub: str
    exp: datetime


class Sessionchema(BaseModel):
    access_token: str
    refresh_token: str


class LoginRequestSchema(RequestSchema):
    username: str
    password: str


class RegisterRequestSchema(RequestSchema):
    username: str
    password: str
    name: str
    image_url: str | None = None


class SessionResponseSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SubscriptionResponseSchema(BaseModel):
    token: str
