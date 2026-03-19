from pydantic import Field
from app.schemas.crud import ReadSchema, CreateSchema, UpdateSchema
from apps.chat.app.modules.message.schemas import ResponseSchema


class OperatorReadSchema(ReadSchema):
    username: str
    name: str
    password_hash: str
    avatar_url: str | None = None


class OperatorCreateSchema(CreateSchema):
    username: str
    name: str
    password_hash: str
    avatar_url: str | None = None


class OperatorUpdateSchema(UpdateSchema):
    name: str | None = None
    avatar_url: str | None = None


class OperatorResponseSchema(ResponseSchema):
    id: int = Field(..., description="Идентификатор оператора")
    username: str = Field(..., description="Логин оператора")
    name: str = Field(..., description="Имя оператора")
    avatar_url: str | None = Field(None, description="URL аватара оператора")
