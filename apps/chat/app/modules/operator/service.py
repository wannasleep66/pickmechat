from typing import Self

from loguru import logger

from app.modules.operator.repository import OperatorRepository
from app.modules.operator.schemas import OperatorCreateSchema, OperatorReadSchema
from app.exceptions import ModelNotFoundException


class OperatorService:
    def __init__(self: Self, operator_repository: OperatorRepository) -> None:
        self.operator_repository = operator_repository

    async def create(
        self: Self, operator_create: OperatorCreateSchema
    ) -> OperatorReadSchema:
        operator = await self.operator_repository.create(operator_create)
        logger.info("Created operator {operator_id}", operator_id=operator.id)
        return operator

    async def get(self: Self, operator_id: int) -> OperatorReadSchema:
        operator = await self.operator_repository.get(operator_id)
        if not operator:
            raise ModelNotFoundException()
        return operator

    async def get_by_username(self: Self, username: str) -> OperatorReadSchema:
        operator = await self.operator_repository.get_by(username=username)
        if not operator:
            raise ModelNotFoundException()
        return operator

    async def exists_with_username(self: Self, username: str) -> bool:
        return await self.operator_repository.exists_with(username=username)

    async def get_all(self: Self) -> list[OperatorReadSchema]:
        return await self.operator_repository.get_all()
