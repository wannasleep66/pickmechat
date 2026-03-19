from typing import Self

from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from faststream.rabbit import RabbitBroker
from sqlalchemy.ext.asyncio.session import AsyncSession
from typing_extensions import AsyncIterable

from app.database import make_session_factory
from app.modules.assigment.di import ModuleProvider as AssigmentModuleProvider
from app.modules.auth.di import ModuleProvider as AuthModuleProvider
from app.modules.conversation.di import ModuleProvider as ConversationModuleProvider
from app.modules.message.di import ModuleProvider as MessageModuleProvider
from app.modules.operator.di import ModuleProvider as OperatorModuleProvider
from app.modules.realtime.di import ModuleProvider as RealtimeModuleProvider
from app.settings import (
    AuthSettings,
    BrokerSettings,
    DatabaseSettings,
    RealtimeTransportSettings,
    Settings,
)


class SessionProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def session(
        self: Self, settings: DatabaseSettings
    ) -> AsyncIterable[AsyncSession]:
        async with make_session_factory(dsn=settings.url)() as session:
            async with session.begin():
                yield session


class SettingsProvider(Provider):
    scope = Scope.APP

    @provide
    async def app(self: Self) -> Settings:
        return Settings()

    @provide
    async def database(self: Self, settings: Settings) -> DatabaseSettings:
        return settings.database

    @provide
    async def broker(self: Self, settings: Settings) -> BrokerSettings:
        return settings.broker

    @provide
    async def auth(self: Self, settings: Settings) -> AuthSettings:
        return settings.auth

    @provide
    async def realtime(self: Self, settings: Settings) -> RealtimeTransportSettings:
        return settings.realtime


class BrokerProvider(Provider):
    scope = Scope.APP

    @provide
    async def broker(self: Self, settings: BrokerSettings) -> RabbitBroker:
        return RabbitBroker(url=settings.url)


def make_container(*providers: Provider) -> AsyncContainer:
    return make_async_container(
        *providers,
        SettingsProvider(),
        SessionProvider(),
        BrokerProvider(),
        ConversationModuleProvider(),
        MessageModuleProvider(),
        RealtimeModuleProvider(),
        OperatorModuleProvider(),
        AuthModuleProvider(),
        AssigmentModuleProvider(),
    )
