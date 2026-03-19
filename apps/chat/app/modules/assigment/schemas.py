from datetime import datetime
from typing import Any, Self

from pydantic import Field
from pydantic.config import ExtraValues
from pydantic.main import BaseModel

from app.modules.assigment.model import Assigment
from app.modules.operator.schemas import OperatorReadSchema, OperatorResponseSchema
from app.schemas.crud import CreateSchema, ReadSchema, UpdateSchema
from app.schemas.request_response import ResponseSchema


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


class AssigmentOutSchema(BaseModel):
    id: int
    operator: OperatorReadSchema
    conversation_id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    @classmethod
    def model_validate(
        cls,
        obj: Assigment,
        *,
        strict: bool | None = None,
        extra: ExtraValues | None = None,
        from_attributes: bool | None = None,
        context: Any | None = None,
        by_alias: bool | None = None,
        by_name: bool | None = None,
    ) -> Self:
        return super().model_validate(
            cls(
                id=obj.id,
                operator=OperatorReadSchema.model_validate(obj.operator),
                conversation_id=obj.conversation_id,
                created_at=obj.created_at,
                updated_at=obj.updated_at,
                deleted_at=obj.deleted_at,
            ).model_dump(),
            strict=strict,
            extra=extra,
            from_attributes=from_attributes,
            context=context,
            by_alias=by_alias,
            by_name=by_name,
        )


class AssigmentResponseSchema(ResponseSchema):
    id: int = Field(..., description="Идентификатор назначения")
    operator: OperatorResponseSchema
    conversation_id: int = Field(..., description="Идентификатор диалога")
    created_at: datetime = Field(..., description="Время создания назначения")
    deleted_at: datetime | None = Field(
        ..., description="Время отзыва назначения с оператора"
    )
