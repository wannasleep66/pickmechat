from common.constants.rabbitmq import ChatExchange, ChatRoutingKeys
from common.schemas.message import (
    DeliveryStatus,
    DeliveryStatusSchema,
    OutgoingMessageSchema,
)
from dishka.integrations.faststream import FromDishka, inject
from faststream.rabbit import RabbitQueue, RabbitRouter
from tenacity import AsyncRetrying, RetryError, wait_exponential
from tenacity.stop import stop_after_attempt

from app.modules.message.service import MessageService

consumer = RabbitRouter()
publisher = consumer.publisher()


@consumer.subscriber(
    exchange=ChatExchange,
    queue=RabbitQueue(ChatRoutingKeys.outgoing(source="telegram")),
)
@inject
async def outbound_message_handler(
    message: OutgoingMessageSchema,
    message_service: FromDishka[MessageService],
) -> None:
    delivery_status: DeliveryStatus

    try:
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(5),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            reraise=True,
        ):
            with attempt:
                await message_service.send_to_client(message)

        delivery_status = "delivered"

    except (Exception, RetryError):
        delivery_status = "failed"

    await publisher.publish(
        DeliveryStatusSchema(
            internal_message_id=message.internal_id, status=delivery_status
        ).model_dump(),
        exchange=ChatExchange,
        routing_key=ChatRoutingKeys.delivery_status(),
    )
