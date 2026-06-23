from typing import Self

from aiogram import Bot
from dishka import Provider, Scope, provide
from faststream.rabbit import RabbitBroker

from app.modules.message.services.attachment import AttachmentService
from app.modules.message.services.message import MessageService
from app.modules.storage.gateway import StorageGateway


class ModuleProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def attachment_service(
        self: Self, bot: Bot, storage_gateway: StorageGateway
    ) -> AttachmentService:
        return AttachmentService(bot=bot, storage_gateway=storage_gateway)

    @provide(scope=Scope.REQUEST)
    def message_service(
        self: Self, broker: RabbitBroker, bot: Bot, storage_gateway: StorageGateway
    ) -> MessageService:
        return MessageService(bot=bot, broker=broker, storage_gateway=storage_gateway)
