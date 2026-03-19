from typing import Self

from aiogram import Bot
from common.constants.rabbitmq import ChatExchange, ChatRoutingKeys
from common.schemas.message import IncomingMessageSchema, OutgoingMessageSchema
from faststream.rabbit.annotations import RabbitBroker
from loguru import logger


class MessageService:
    def __init__(self: Self, *, bot: Bot, broker: RabbitBroker) -> None:
        self.bot = bot
        self.broker = broker

    async def send_to_client(self: Self, message: OutgoingMessageSchema) -> None:
        await self.bot.send_message(
            chat_id=message.to.external_id,
            text=message.content.text,
        )
        logger.info(
            "Sent message to user {user_id} from operator {operator_id}",
            user_id=message.to.external_id,
            operator_id=message.sender.external_id,
        )

    async def send_to_operator(self: Self, message: IncomingMessageSchema) -> None:
        await self.broker.publish(
            message.model_dump(),
            exchange=ChatExchange,
            routing_key=ChatRoutingKeys.incoming("telegram"),
        )
        logger.info(
            "Sent message to operator from user {user_id}",
            user_id=message.sender.external_id,
        )
