from typing import Self

from dishka import Provider, Scope, provide

from app.modules.realtime.transport import RealtimeTransport
from app.settings import RealtimeTransportSettings


class ModuleProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def realtime_transport(
        self: Self, settings: RealtimeTransportSettings
    ) -> RealtimeTransport:
        return RealtimeTransport(settings=settings)
