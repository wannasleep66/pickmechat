from pydantic import BaseModel

from app.schemas.crud import CreateSchema, ReadSchema, UpdateSchema
from apps.chat.app.schemas.request_response import RequestSchema, ResponseSchema


class LastReadReadSchema(ReadSchema):
    conversation_id: int
    operator_id: int
    message_id: int


class LastReadCreateSchema(CreateSchema):
    conversation_id: int
    operator_id: int
    message_id: int


class LastReadUpdateSchema(UpdateSchema):
    message_id: int


class LastReadOutSchema(LastReadReadSchema): ...


class LastReadInSchema(BaseModel):
    conversation_id: int
    message_id: int


class LastReadResponseSchema(ResponseSchema, LastReadOutSchema): ...


class LastReadRequestSchema(RequestSchema):
    message_id: int
