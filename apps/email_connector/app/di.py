from typing import Any, Self, cast

from dishka import (
    AsyncContainer,
    Provider,
    Scope,
    make_async_container,
    provide,
)
from faststream._internal.types import BrokerMiddleware
from faststream.rabbit import RabbitBroker
from faststream.rabbit.prometheus.middleware import RabbitPrometheusMiddleware
from prometheus_client import CollectorRegistry

from app.modules.message.di import ModuleProvider as MessageModuleProvider
from app.settings import AppSettings, BrokerSettings, EmailSettings, Settings


class SettingsProvider(Provider):
    scope = Scope.APP

    @provide
    def settings(self: Self) -> Settings:
        return Settings()

    @provide
    async def app(self: Self, settings: Settings) -> AppSettings:
        return settings.app

    @provide
    def broker(self: Self, settings: Settings) -> BrokerSettings:
        return settings.broker

    @provide
    def email(self: Self, settings: Settings) -> EmailSettings:
        return settings.email


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


def make_container(*providers: Provider) -> AsyncContainer:
    return make_async_container(
        *providers,
        SettingsProvider(),
        MonitoringRegistryProvider(),
        BrokerProvider(),
        MessageModuleProvider(),
    )
