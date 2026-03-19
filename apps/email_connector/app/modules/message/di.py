from typing import Self

from dishka import Provider, Scope, provide
from faststream.rabbit import RabbitBroker

from app.modules.message.mailer import Mailer
from app.modules.message.service import MessageService
from app.settings import EmailSettings


class ModuleProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def mailer(self: Self, settings: EmailSettings) -> Mailer:
        return Mailer(settings=settings)

    @provide(scope=Scope.REQUEST)
    def message_service(
        self: Self, mailer: Mailer, broker: RabbitBroker
    ) -> MessageService:
        return MessageService(broker=broker, mailer=mailer)
