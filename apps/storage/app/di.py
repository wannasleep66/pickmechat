from typing import AsyncGenerator, Self

from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import make_session_factory
from app.settings import DatabaseSettings, Settings


class SessionProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def session(
        self: Self, settings: DatabaseSettings
    ) -> AsyncGenerator[AsyncSession]:
        async with make_session_factory(dsn=settings.url)() as session:
            async with session.begin():
                yield session


class SettingsProvider(Provider):
    scope = Scope.APP

    @provide
    def app(self: Self) -> Settings:
        return Settings()

    @provide
    def database(self: Self, settings: Settings) -> DatabaseSettings:
        return settings.database


def make_container(*providers: Provider) -> AsyncContainer:
    return make_async_container(
        *providers,
        SettingsProvider(),
        SessionProvider(),
    )
