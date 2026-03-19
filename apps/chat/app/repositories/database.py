from datetime import datetime
from typing import Generic, Self, TypeVar

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Base
from app.schemas.crud import CreateSchema, ReadSchema, UpdateSchema

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=CreateSchema)
ReadSchemaType = TypeVar("ReadSchemaType", bound=ReadSchema)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=UpdateSchema)


class DatabaseRepository(
    Generic[ModelType, CreateSchemaType, ReadSchemaType, UpdateSchemaType]
):
    """Базовый репозиторий для работы с базой данных"""

    __abstract__: bool = True
    model_type: type[ModelType]
    model_schema: type[ReadSchemaType]

    def __init__(self: Self, session: AsyncSession) -> None:
        self.session = session

    async def get(
        self: Self, id_: int, with_deleted: bool = False
    ) -> ReadSchemaType | None:
        stmt = select(self.model_type).filter_by(id=id_)
        if not with_deleted and self.model_type.soft_deletable:
            stmt = stmt.filter_by(deleted_at=None)
        instance = await self.session.scalar(stmt)
        return self.model_schema.model_validate(instance) if instance else None

    async def get_by(
        self: Self, with_deleted: bool = False, **filters: object
    ) -> ReadSchemaType | None:
        stmt = select(self.model_type).filter_by(**filters)
        if not with_deleted and self.model_type.soft_deletable:
            stmt = stmt.filter_by(deleted_at=None)
        instance = await self.session.scalar(stmt)
        return self.model_schema.model_validate(instance) if instance else None

    async def exists_with(
        self: Self,
        except_id: int | None = None,
        with_deleted: bool = False,
        **filters: object,
    ) -> bool:
        stmt = select(self.model_type).filter_by(**filters)
        if not with_deleted and self.model_type.soft_deletable:
            stmt = stmt.filter_by(deleted_at=None)
        if except_id:
            stmt = stmt.filter(self.model_type.id != except_id)
        return await self.session.scalar(stmt) is not None

    async def get_all(self: Self, with_deleted: bool = False) -> list[ReadSchemaType]:
        stmt = select(self.model_type)
        if not with_deleted and self.model_type.soft_deletable:
            stmt = stmt.filter_by(deleted_at=None)
        instances = await self.session.scalars(stmt)
        return [self.model_schema.model_validate(ins) for ins in instances]

    async def get_all_by(
        self: Self, with_deleted: bool = False, **filters: object
    ) -> list[ReadSchemaType]:
        stmt = select(self.model_type).filter_by(**filters)
        if not with_deleted and self.model_type.soft_deletable:
            stmt = stmt.filter_by(deleted_at=None)
        instances = await self.session.scalars(stmt)
        return [self.model_schema.model_validate(ins) for ins in instances]

    async def create(self: Self, create_data: CreateSchemaType) -> ReadSchemaType:
        stmt = (
            insert(self.model_type)
            .values(create_data.model_dump())
            .returning(self.model_type)
        )
        instance = await self.session.scalar(stmt)
        return self.model_schema.model_validate(instance)

    async def update(
        self: Self, id_: int, update_data: UpdateSchemaType
    ) -> ReadSchemaType:
        stmt = (
            update(self.model_type)
            .filter_by(id=id_)
            .values(update_data.model_dump(exclude_none=True))
            .returning(self.model_type)
        )
        updated_instance = await self.session.scalar(stmt)
        return self.model_schema.model_validate(updated_instance)

    async def delete(self: Self, id_: int) -> int | None:
        stmt = delete(self.model_type).filter_by(id=id_).returning(self.model_type.id)
        result = await self.session.scalar(stmt)
        return result

    async def soft_delete(self: Self, id_: int) -> int | None:
        assert self.model_type.soft_deletable
        now = datetime.now()
        stmt = (
            update(self.model_type)
            .filter_by(id=id_)
            .values({"deleted_at": now})
            .returning(self.model_type.id)
        )
        result = await self.session.scalar(stmt)
        return result

    async def recover(self: Self, id_: int) -> ReadSchemaType:
        assert self.model_type.soft_deletable
        stmt = (
            update(self.model_type)
            .filter_by(id=id_)
            .values({"deleted_at": None})
            .returning(self.model_type)
        )
        updated_instance = await self.session.scalar(stmt)
        return self.model_schema.model_validate(updated_instance)

    async def delete_by(
        self: Self, except_id: int | None = None, **conditions: object
    ) -> list[int]:
        stmt = (
            delete(self.model_type)
            .filter_by(**conditions)
            .returning(self.model_type.id)
        )
        if except_id:
            stmt = stmt.filter(self.model_type.id != except_id)
        results = await self.session.scalars(stmt)
        return list(results)

    async def soft_delete_by(
        self: Self, except_id: int | None = None, **conditions: object
    ) -> list[int]:
        assert self.model_type.soft_deletable
        now = datetime.now()
        stmt = (
            update(self.model_type)
            .filter_by(**conditions)
            .values({"deleted_at": now})
            .returning(self.model_type.id)
        )
        results = await self.session.scalars(stmt)
        return list(results)
