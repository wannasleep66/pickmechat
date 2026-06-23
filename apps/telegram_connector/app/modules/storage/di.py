from typing import Self

from dishka import Provider, Scope, provide

from app.modules.storage.gateway import StorageGateway
from app.settings import GatewaysSettings


class ModuleProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def storage_gateway(self: Self, settings: GatewaysSettings) -> StorageGateway:
        return StorageGateway(url=settings.storage_url)
