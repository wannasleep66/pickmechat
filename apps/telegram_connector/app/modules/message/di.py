from typing import Self

from aiogram import Bot
from dishka import Provider, Scope, provide
from faststream.rabbit import RabbitBroker

from app.gateways.storage import StorageGateway
from app.modules.message.services.attachment import AttachmentService
from app.modules.message.services.message import MessageService


class ModuleProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def attachment_service(
        self: Self, bot: Bot, storage_gateway: StorageGateway
    ) -> AttachmentService:
        return AttachmentService(bot=bot, storage_gateway=storage_gateway)

    @provide(scope=Scope.REQUEST)
    def message_service(self: Self, broker: RabbitBroker, bot: Bot) -> MessageService:
        return MessageService(bot=bot, broker=broker)
