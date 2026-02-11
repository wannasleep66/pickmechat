from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.settings import DatabaseSettings

POSTGRES_INDEXES_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}

metadata = MetaData(naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION)


def make_async_engine(dsn: str, echo: bool = False) -> AsyncEngine:
    """
    Создание асинхронного движка
    """
    return create_async_engine(dsn, echo=echo)


def make_session_factory(
    dsn: str, echo: bool = False
) -> async_sessionmaker[AsyncSession]:
    """
    Создание фабрики асинхронных сессий
    """
    return async_sessionmaker(
        bind=make_async_engine(dsn, echo=echo),
        autoflush=False,
        expire_on_commit=False,
    )


@asynccontextmanager
async def session_context() -> AsyncGenerator[AsyncSession, None]:
    """
    Конекстный менеджер для получения сессии
    """

    async with make_session_factory(DatabaseSettings().url, echo=False)() as session:
        async with session.begin():
            yield session


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__: bool = True

    id: Mapped[int] = mapped_column(primary_key=True)

    metadata = metadata
