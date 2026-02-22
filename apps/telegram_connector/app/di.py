from typing import Self

from aiogram import Bot
from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from faststream.rabbit import RabbitBroker

from app.settings import BotSettings, BrokerSettings, Settings
from app.modules.message.di import ModuleProvider as MessageModuleProvider


class SettingsProvider(Provider):
    scope = Scope.APP

    @provide
    async def settings(self: Self) -> Settings:
        return Settings()

    @provide
    async def broker(self: Self, settings: Settings) -> BrokerSettings:
        return settings.broker

    @provide
    async def bot(self: Self, settings: Settings) -> BotSettings:
        return settings.bot


class BrokerProvider(Provider):
    scope = Scope.APP

    @provide
    def broker(self: Self, settings: BrokerSettings) -> RabbitBroker:
        return RabbitBroker(url=settings.url)


class BotProvider(Provider):
    scope = Scope.APP

    @provide
    def bot(self: Self, settings: BotSettings) -> Bot:
        return Bot(token=settings.token)


def make_container(*providers: Provider) -> AsyncContainer:
    return make_async_container(
        *providers,
        SettingsProvider(),
        BrokerProvider(),
        BotProvider(),
        MessageModuleProvider(),
    )
