from typing import Self

from faststream.rabbit import RabbitBroker
from loguru import logger
from common.schemas.message import MessageSchema
from common.constants.rabbitmq import ChatExchange, ChatRoutingKeys

from app.modules.message.services.mailer import Mailer


class MessageService:
    def __init__(self: Self, *, broker: RabbitBroker, mailer: Mailer) -> None:
        self.broker = broker
        self.mailer = mailer

    async def send_to_client(self: Self, message: MessageSchema) -> None:
        await self.mailer.send(
            message=message.content.text,
            subject="Техподдержка",
            recepient=message.sender.external_id,
        )
        logger.info("Sent email to user {user_id}", user_id=message.sender.external_id)

    async def send_to_operator(self: Self, message: MessageSchema) -> None:
        await self.broker.publish(
            message.model_dump(),
            exchange=ChatExchange,
            routing_key=ChatRoutingKeys.incoming("email"),
        )
        logger.info(
            "Sent message to operator from user {user_id}",
            user_id=message.sender.external_id,
        )
