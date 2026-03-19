from typing import Self

from common.constants.rabbitmq import ChatExchange, ChatRoutingKeys
from common.schemas.message import IncomingMessageSchema, OutgoingMessageSchema
from faststream.rabbit import RabbitBroker
from loguru import logger

from app.modules.message.mailer import Mailer


class MessageService:
    def __init__(self: Self, *, broker: RabbitBroker, mailer: Mailer) -> None:
        self.broker = broker
        self.mailer = mailer

    async def send_to_client(self: Self, message: OutgoingMessageSchema) -> None:
        await self.mailer.send(
            message=message.content.text,
            subject="Техподдержка",
            recepient=message.to.external_id,
        )
        logger.info(
            "Sent email to user {user_id} from operator {operator_id}",
            user_id=message.to.external_id,
            operator_id=message.sender.external_id,
        )

    async def send_to_operator(self: Self, message: IncomingMessageSchema) -> None:
        await self.broker.publish(
            message.model_dump(),
            exchange=ChatExchange,
            routing_key=ChatRoutingKeys.incoming("email"),
        )
        logger.info(
            "Sent message to operator from user {user_id}",
            user_id=message.sender.external_id,
        )
