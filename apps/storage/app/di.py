from typing import AsyncGenerator, Callable, Self

from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import make_session_factory
from app.modules.file.di import ModuleProvider as FileModuleProvider
from app.repositories.storage import StorageRepository
from app.repositories.storage.s3 import S3StorageParams, S3StorageRepository
from app.settings import DatabaseSettings, Settings, StorageSettings
from apps.storage.app.repositories.storage.local import (
    LocalStorageParams,
    LocalStorageRepository,
)


class SessionProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def session(
        self: Self, settings: DatabaseSettings
    ) -> AsyncGenerator[AsyncSession]:
        async with make_session_factory(dsn=settings.url)() as session:
            async with session.begin():
                yield session


class StorageProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def storage_repository(
        self: Self,
        settings: StorageSettings,
    ) -> StorageRepository:
        factory: Callable[[], StorageRepository] = {
            "s3": lambda: S3StorageRepository(
                S3StorageParams(**settings.s3.model_dump()),
            ),
            "local": lambda: LocalStorageRepository(
                LocalStorageParams(**settings.local.model_dump())
            ),
        }[settings.provider]

        return factory()


class SettingsProvider(Provider):
    scope = Scope.APP

    @provide
    def app(self: Self) -> Settings:
        return Settings()

    @provide
    def database(self: Self, settings: Settings) -> DatabaseSettings:
        return settings.database

    @provide
    def storage(self: Self, settings: Settings) -> StorageSettings:
        return settings.storage


def make_container(*providers: Provider) -> AsyncContainer:
    return make_async_container(
        *providers,
        SettingsProvider(),
        SessionProvider(),
        StorageProvider(),
        FileModuleProvider(),
    )
