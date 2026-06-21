from typing import Self

from loguru import logger

from app.exceptions import ModelNotFoundException
from app.modules.operator.repositories.availability_status import (
    AvailabilityStatusRepository,
)
from app.modules.operator.repositories.operator import OperatorRepository
from app.modules.operator.schemas.availability_status import (
    AvailabilityStatus,
    AvailabilityStatusOutSchema,
    AvailabilityStatusUpdateSchema,
)
from app.modules.operator.schemas.operator import (
    OperatorCreateSchema,
    OperatorDetailsOutSchema,
    OperatorOutSchema,
    OperatorReadSchema,
    OperatorUpdateSchema,
)
from app.modules.realtime.events import (
    AvailabilityStatusChanged,
    AvailabilityStatusChangedPayload,
)
from app.modules.realtime.transport import RealtimeTransport


class OperatorService:
    def __init__(
        self: Self,
        operator_repository: OperatorRepository,
        status_repository: AvailabilityStatusRepository,
        realtime_transport: RealtimeTransport,
    ) -> None:
        self.operator_repository = operator_repository
        self.status_repository = status_repository
        self.realtime_transport = realtime_transport

    async def create(
        self: Self, operator_create: OperatorCreateSchema
    ) -> OperatorReadSchema:
        operator = await self.operator_repository.create(operator_create)
        logger.info("Created operator {operator_id}", operator_id=operator.id)
        return operator

    async def update(
        self: Self, operator: OperatorOutSchema, operator_update: OperatorUpdateSchema
    ) -> OperatorDetailsOutSchema:
        operator_to_update = await self.get(operator.id)
        updated_operator = await self.operator_repository.update(
            operator_to_update.id, operator_update
        )
        logger.info(
            "Updated operator {operator_id} from {before} to {after}",
            operator_id=updated_operator.id,
            before={
                k: getattr(operator_to_update, k)
                for k in operator_update.model_dump(exclude_none=True).keys()
            },
            after={
                k: getattr(updated_operator, k)
                for k in operator_update.model_dump(exclude_none=True).keys()
            },
        )
        return await self.get_details(updated_operator.id)

    async def change_availability(
        self: Self, operator: OperatorOutSchema, status: AvailabilityStatus
    ) -> AvailabilityStatusOutSchema:
        operator_to_update = await self.get(operator.id)
        updated_status = await self.status_repository.upsert_by_operator(
            operator_to_update.id, AvailabilityStatusUpdateSchema(status=status)
        )
        operators = await self.get_all()
        await self.realtime_transport.broadcast(
            [f"personal:{op.id}" for op in operators],
            AvailabilityStatusChanged(
                payload=AvailabilityStatusChangedPayload(
                    operator_id=operator_to_update.id, status=updated_status.status
                )
            ),
        )
        logger.info(
            "Set operator {operator_id} availability status {status}",
            operator_id=operator_to_update.id,
            status=updated_status.status,
        )
        return AvailabilityStatusOutSchema(**updated_status.model_dump())

    async def get(self: Self, operator_id: int) -> OperatorOutSchema:
        operator = await self.operator_repository.get(operator_id)
        if not operator:
            raise ModelNotFoundException()
        return operator

    async def get_by_username(self: Self, username: str) -> OperatorReadSchema:
        operator = await self.operator_repository.get_by(username=username)
        if not operator:
            raise ModelNotFoundException()
        return operator

    async def get_details(self: Self, operator_id: int) -> OperatorDetailsOutSchema:
        operator = await self.operator_repository.get_details(operator_id)
        if not operator:
            raise ModelNotFoundException()
        return operator

    async def get_all(
        self: Self, search: str | None = None
    ) -> list[OperatorDetailsOutSchema]:
        return await self.operator_repository.get_all_detailed(search=search)

    async def exists_with_username(self: Self, username: str) -> bool:
        return await self.operator_repository.exists_with(username=username)
