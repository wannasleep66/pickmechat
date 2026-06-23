import asyncio

from common.constants.rabbitmq import ChatExchange, ChatRoutingKeys
from common.schemas.message import (
    DeliveryStatus,
    DeliveryStatusSchema,
    OutgoingMessageSchema,
)
from dishka.integrations.faststream import FromDishka, inject
from faststream.rabbit import RabbitQueue, RabbitRouter
from loguru import logger
from tenacity import AsyncRetrying, RetryError
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_fixed

from app.modules.message.services.message import MessageService

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
            wait=wait_fixed(1),
            reraise=True,
        ):
            with attempt:
                logger.debug(
                    "Trying to send message to user attempt={attempt}",
                    attempt=attempt.retry_state.attempt_number,
                )
                await asyncio.wait_for(
                    message_service.send_to_client(message), timeout=15
                )

        delivery_status = "delivered"

    except (Exception, RetryError):
        delivery_status = "failed"
        logger.error(
            "Failed to send message to user {user_id} from operator {operator_id}",
            user_id=message.to.external_id,
            operator_id=message.sender.external_id,
        )

    await publisher.publish(
        DeliveryStatusSchema(
            internal_message_id=message.internal_id, status=delivery_status
        ).model_dump(),
        exchange=ChatExchange,
        routing_key=ChatRoutingKeys.delivery_status(),
    )
