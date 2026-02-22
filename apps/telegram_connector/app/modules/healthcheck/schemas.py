from typing import Literal

from pydantic import BaseModel


HealthCheckStatus = Literal["working", "error"]


class HealthCheckResponseSchema(BaseModel):
    status: HealthCheckStatus
