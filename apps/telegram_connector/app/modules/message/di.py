from typing import Self
from aiogram import Bot
from dishka import Provider, Scope, provide
from faststream.rabbit import RabbitBroker

from app.modules.message.service import MessageService


class ModuleProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def message_service(self: Self, broker: RabbitBroker, bot: Bot) -> MessageService:
        return MessageService(bot=bot, broker=broker)
