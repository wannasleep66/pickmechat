from typing import Literal

from pydantic import Field

from app.schemas.request_response import ResponseSchema

type HealthCheckStatus = Literal["ok", "error"]


class HealthCheckResponseSchema(ResponseSchema):
    status: HealthCheckStatus = Field(description="Статус состояния системы")
