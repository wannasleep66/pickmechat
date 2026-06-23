from typing import Any, Self, cast

from aiogram import Bot
from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from faststream._internal.types import BrokerMiddleware
from faststream.rabbit import RabbitBroker
from faststream.rabbit.prometheus.middleware import RabbitPrometheusMiddleware
from prometheus_client import CollectorRegistry

from app.modules.message.di import ModuleProvider as MessageModuleProvider
from app.modules.storage.di import ModuleProvider as StorageModuleProvider
from app.settings import (
    AppSettings,
    BotSettings,
    BrokerSettings,
    GatewaysSettings,
    Settings,
)


class SettingsProvider(Provider):
    scope = Scope.APP

    @provide
    def settings(self: Self) -> Settings:
        return Settings()

    @provide
    def app(self: Self, settings: Settings) -> AppSettings:
        return settings.app

    @provide
    def broker(self: Self, settings: Settings) -> BrokerSettings:
        return settings.broker

    @provide
    def bot(self: Self, settings: Settings) -> BotSettings:
        return settings.bot

    @provide
    def gateways(self: Self, settings: Settings) -> GatewaysSettings:
        return settings.gateways


class MonitoringRegistryProvider(Provider):
    scope = Scope.APP

    @provide
    def registry(self: Self) -> CollectorRegistry:
        return CollectorRegistry()


class BrokerProvider(Provider):
    scope = Scope.APP

    @provide
    def middlewares(
        self: Self, monitoring_registry: CollectorRegistry, settings: AppSettings
    ) -> list[BrokerMiddleware]:
        return cast(
            list[BrokerMiddleware[Any, Any]],
            [
                RabbitPrometheusMiddleware(
                    registry=monitoring_registry, app_name=settings.name
                )
            ],
        )

    @provide
    def broker(
        self: Self, settings: BrokerSettings, middlewares: list[BrokerMiddleware]
    ) -> RabbitBroker:
        return RabbitBroker(url=settings.url, middlewares=middlewares)


class BotProvider(Provider):
    scope = Scope.APP

    @provide
    def bot(self: Self, settings: BotSettings) -> Bot:
        return Bot(token=settings.token)


def make_container(*providers: Provider) -> AsyncContainer:
    return make_async_container(
        *providers,
        SettingsProvider(),
        MonitoringRegistryProvider(),
        BrokerProvider(),
        BotProvider(),
        StorageModuleProvider(),
        MessageModuleProvider(),
    )
