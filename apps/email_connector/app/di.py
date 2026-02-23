from typing import Self
from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from faststream.rabbit import RabbitBroker

from app.settings import BrokerSettings, EmailSettings, Settings
from app.modules.message.di import ModuleProvider as MessageModuleProvider


class SettingsProvider(Provider):
    scope = Scope.APP

    @provide
    def settings(self: Self) -> Settings:
        return Settings()

    @provide
    def broker(self: Self, settings: Settings) -> BrokerSettings:
        return settings.broker

    @provide
    def email(self: Self, settings: Settings) -> EmailSettings:
        return settings.email


class BrokerProvider(Provider):
    scope = Scope.APP

    @provide
    def broker(self: Self, settings: BrokerSettings) -> RabbitBroker:
        return RabbitBroker(url=settings.url)


def make_container(*providers: Provider) -> AsyncContainer:
    return make_async_container(
        *providers,
        SettingsProvider(),
        BrokerProvider(),
        MessageModuleProvider(),
    )
