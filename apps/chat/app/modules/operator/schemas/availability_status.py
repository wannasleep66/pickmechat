from datetime import datetime
from typing import Literal

from pydantic import Field

from app.schemas.crud import CreateSchema, ReadSchema, UpdateSchema
from app.schemas.request_response import ResponseSchema

type AvailabilityStatus = Literal["available", "away", "dnd"]


class AvailabilityStatusReadSchema(ReadSchema):
    status: AvailabilityStatus
    operator_id: int
    updated_at: datetime


class AvailabilityStatusCreateSchema(CreateSchema):
    status: AvailabilityStatus
    operator_id: int


class AvailabilityStatusUpdateSchema(UpdateSchema):
    status: AvailabilityStatus


class AvailabilityStatusOutSchema(ReadSchema):
    status: AvailabilityStatus
    updated_at: datetime


class AvailabilityStatusResponseSchema(ResponseSchema):
    status: AvailabilityStatus = Field(description="Статус доступности оператора")
    updated_at: datetime
