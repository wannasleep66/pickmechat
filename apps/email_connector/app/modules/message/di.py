from typing import Self

from dishka import Provider, provide, Scope
from faststream.rabbit import RabbitBroker

from app.settings import EmailSettings
from app.modules.message.services.mailer import Mailer
from app.modules.message.services.message import MessageService


class ModuleProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def mailer(self: Self, settings: EmailSettings) -> Mailer:
        return Mailer(settings=settings)

    @provide(scope=Scope.REQUEST)
    def message_service(
        self: Self, mailer: Mailer, broker: RabbitBroker
    ) -> MessageService:
        return MessageService(broker=broker, mailer=mailer)
