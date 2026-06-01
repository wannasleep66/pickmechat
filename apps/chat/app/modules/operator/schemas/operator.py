from datetime import datetime
from typing import Any, Self

from pydantic import Field
from pydantic.config import ExtraValues

from app.modules.operator.models.operator import Operator
from app.modules.operator.schemas.availability_status import (
    AvailabilityStatus,
    AvailabilityStatusOutSchema,
    AvailabilityStatusResponseSchema,
)
from app.schemas.crud import CreateSchema, ReadSchema, UpdateSchema
from app.schemas.request_response import RequestSchema, ResponseSchema


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


class OperatorOutSchema(ReadSchema):
    username: str
    name: str
    avatar_url: str | None = None
    availability: AvailabilityStatusOutSchema | None = None

    @classmethod
    def model_validate(
        cls: type[Self],
        obj: Operator,
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
                username=obj.username,
                name=obj.name,
                avatar_url=obj.avatar_url,
                availability=AvailabilityStatusOutSchema.model_validate(obj.status)
                if obj.status
                else None,
            ).model_dump(),
            strict=strict,
            extra=extra,
            from_attributes=from_attributes,
            context=context,
            by_alias=by_alias,
            by_name=by_name,
        )


class OperatorAssigmentOutSchema(ReadSchema):
    id: int
    conversation_id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class OperatorDetailsOutSchema(OperatorOutSchema):
    assigments: list[OperatorAssigmentOutSchema]

    @classmethod
    def model_validate(
        cls: type[Self],
        obj: Operator,
        *,
        strict: bool | None = None,
        extra: ExtraValues | None = None,
        from_attributes: bool | None = None,
        context: Any | None = None,
        by_alias: bool | None = None,
        by_name: bool | None = None,
    ) -> Self:
        return super(OperatorOutSchema, cls).model_validate(
            cls(
                **OperatorOutSchema.model_validate(obj).model_dump(),
                assigments=[
                    OperatorAssigmentOutSchema.model_validate(ass)
                    for ass in obj.assigments
                ],
            ).model_dump(),
            strict=strict,
            extra=extra,
            from_attributes=from_attributes,
            context=context,
            by_alias=by_alias,
            by_name=by_name,
        )


class OperatorResponseSchema(ResponseSchema):
    id: int = Field(..., description="Идентификатор оператора")
    username: str = Field(..., description="Логин оператора")
    name: str = Field(..., description="Имя оператора")
    avatar_url: str | None = Field(None, description="URL аватара оператора")
    availability: AvailabilityStatusResponseSchema | None = Field(
        None, description="Статус доступности пользователя"
    )


class OperatorAssigmentResponseSchema(ResponseSchema):
    id: int = Field(..., description="Идентификатор назначения")
    conversation_id: int = Field(..., description="Идентификатор диалога")
    created_at: datetime = Field(..., description="Время создания назначения")
    deleted_at: datetime | None = Field(
        ..., description="Время отзыва назначения с оператора"
    )


class OperatorDetailsResponseSchema(OperatorResponseSchema):
    assigments: list[OperatorAssigmentResponseSchema] = Field(
        default_factory=list, description="Назначенния оператора"
    )


class OperatorUpdateRequestSchema(OperatorUpdateSchema, RequestSchema): ...


class OperatorChangeAvailabilityRequestSchema(RequestSchema):
    status: AvailabilityStatus
