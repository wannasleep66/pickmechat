from typing import Self

from dishka import Provider, Scope, provide

from app.gateways.storage import StorageGateway
from app.settings import GatewaysSettings


class GatewaysProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def storage(self: Self, settings: GatewaysSettings) -> StorageGateway:
        return StorageGateway(url=settings.storage_url)
