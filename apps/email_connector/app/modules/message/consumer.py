from faststream.rabbit import RabbitRouter, RabbitQueue
from dishka.integrations.faststream import inject

from common.constants.rabbitmq import ChatExchange, ChatRoutingKeys
from common.schemas.message import MessageSchema


consumer = RabbitRouter()


@consumer.subscriber(
    exchange=ChatExchange,
    queue=RabbitQueue(ChatRoutingKeys.outgoing("email")),
)
@inject
async def outbound_message_handler(message: MessageSchema) -> None: ...
