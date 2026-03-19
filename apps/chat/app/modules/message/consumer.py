from common.constants.rabbitmq import ChatExchange, ChatRoutingKeys
from common.schemas.message import DeliveryStatusSchema, IncomingMessageSchema
from dishka.integrations.faststream import FromDishka, inject
from faststream.middlewares import AckPolicy
from faststream.rabbit import RabbitQueue, RabbitRouter

from app.modules.message.service import MessageService

consumer = RabbitRouter()


@consumer.subscriber(
    exchange=ChatExchange,
    queue=RabbitQueue("incoming", routing_key=ChatRoutingKeys.all_incoming()),
    ack_policy=AckPolicy.NACK_ON_ERROR,
)
@inject
async def handle_incoming_message(
    message: IncomingMessageSchema, message_service: FromDishka[MessageService]
) -> None:
    await message_service.send_to_operator(message)


@consumer.subscriber(
    exchange=ChatExchange,
    queue=RabbitQueue(
        "delivery-status",
        routing_key=ChatRoutingKeys.delivery_status(),
        durable=True,
    ),
    ack_policy=AckPolicy.NACK_ON_ERROR,
)
@inject
async def handle_delivery_status(
    message: DeliveryStatusSchema, message_service: FromDishka[MessageService]
) -> None:
    await message_service.update_delivery_status(
        message.internal_message_id, message.status
    )
