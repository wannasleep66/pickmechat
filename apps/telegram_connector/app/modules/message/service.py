from typing import Self

from aiogram import Bot
from faststream.rabbit.annotations import RabbitBroker
from loguru import logger

from common.constants.rabbitmq import ChatExchange, ChatRoutingKeys
from common.schemas.message import MessageSchema


class MessageService:
    def __init__(self: Self, *, bot: Bot, broker: RabbitBroker) -> None:
        self.bot = bot
        self.broker = broker

    async def send_to_client(self: Self, message: MessageSchema) -> None:
        await self.bot.send_message(
            chat_id=message.sender.external_id,
            text=message.content.text,
        )
        logger.info(
            "Sent message from operator to user {user_id}",
            user_id=message.sender.external_id,
        )

    async def send_to_operator(self: Self, message: MessageSchema) -> None:
        await self.broker.publish(
            message.model_dump(),
            exchange=ChatExchange,
            routing_key=ChatRoutingKeys.incoming("telegram"),
        )
        logger.info(
            "Sent message to operator from user {user_id}",
            user_id=message.sender.external_id,
        )
