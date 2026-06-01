from datetime import datetime

from app.schemas.crud import CreateSchema, ReadSchema, UpdateSchema


class AssigmentReadSchema(ReadSchema):
    operator_id: int
    conversation_id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None


class AssigmentCreateSchema(CreateSchema):
    operator_id: int
    conversation_id: int


class AssigmentUpdateSchema(UpdateSchema):
    deleted_at: datetime | None = None


class AssigmentResponseSchema(AssigmentReadSchema): ...
