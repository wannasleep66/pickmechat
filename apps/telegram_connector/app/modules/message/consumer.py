from dishka.integrations.faststream import FromDishka, inject
from faststream.rabbit import RabbitQueue, RabbitRouter

from common.schemas.message import MessageSchema
from common.constants.rabbitmq import ChatExchange, ChatRoutingKeys
from app.modules.message.service import MessageService


consumer = RabbitRouter()


@consumer.subscriber(
    exchange=ChatExchange,
    queue=RabbitQueue(ChatRoutingKeys.outgoing(source="telegram")),
)
@inject
async def outbound_message_handler(
    message: MessageSchema,
    message_service: FromDishka[MessageService],
) -> None:
    await message_service.send_to_client(message)
