from faststream.rabbit import RabbitRouter, RabbitQueue
from dishka.integrations.faststream import inject, FromDishka

from app.modules.message.services.message import MessageService
from common.constants.rabbitmq import ChatExchange, ChatRoutingKeys
from common.schemas.message import MessageSchema


consumer = RabbitRouter()


@consumer.subscriber(
    exchange=ChatExchange,
    queue=RabbitQueue(ChatRoutingKeys.outgoing("email")),
)
@inject
async def outbound_message_handler(
    message: MessageSchema, message_service: FromDishka[MessageService]
) -> None:
    await message_service.send_to_client(message)
