from typing import Self, cast

from common.constants.rabbitmq import ChatExchange, ChatRoutingKeys
from common.schemas.message import (
    DeliveryStatus,
    IncomingMessageSchema,
    MessageContent,
    OutgoingMessageSchema,
)
from common.schemas.user import UserSchema
from faststream.rabbit import RabbitBroker
from loguru import logger

from app.exceptions import PermissionException
from app.modules.assigment.service import AssigmentService
from app.modules.conversation.schemas import ConversationCreateSchema
from app.modules.conversation.service import ConversationService
from app.modules.message.repository import MessageCreateSchema, MessageRepository
from app.modules.message.schemas import (
    MessageInSchema,
    MessageOutSchema,
    MessageSender,
    MessageUpdateSchema,
)
from app.modules.operator.schemas import OperatorReadSchema
from app.modules.realtime.events import (
    DeliveryStatusUpdateEvent,
    DeliveryStatusUpdatePayload,
    NewMessageEvent,
    NewMessageEventPayload,
    NewMessageSchema,
)
from app.modules.realtime.transport import RealtimeTransport
from app.schemas.pagination import Paginated


class MessageService:
    def __init__(
        self: Self,
        *,
        assigment_service: AssigmentService,
        conversation_service: ConversationService,
        realtime_transport: RealtimeTransport,
        message_repository: MessageRepository,
        broker: RabbitBroker,
    ) -> None:
        self.assigment_service = assigment_service
        self.conversation_service = conversation_service
        self.realtime_transport = realtime_transport
        self.message_repository = message_repository
        self.broker = broker

    async def send_to_operator(
        self: Self, incoming_message: IncomingMessageSchema
    ) -> None:
        conversation = await self.conversation_service.get_or_create(
            ConversationCreateSchema(
                title=f"{incoming_message.sender.external_id} {incoming_message.sender.name}",
                channel=incoming_message.source,
                external_user_id=incoming_message.sender.external_id,
            )
        )
        assigments = await self.assigment_service.get_by_conversation(conversation.id)
        message = await self.message_repository.create(
            MessageCreateSchema(
                text=incoming_message.content.text,
                source=incoming_message.source,
                sender_type="user",
                external_user_id=incoming_message.sender.external_id,
                external_user_name=incoming_message.sender.name,
                timestamp=incoming_message.timestamp,
                delivery_status="delivered",
                conversation_id=conversation.id,
            )
        )
        logger.info(
            "External user {external_user_id} created message {message_id}",
            external_user_id=incoming_message.sender.external_id,
            message_id=message.id,
        )
        await self.realtime_transport.broadcast(
            channels=[f"personal:{ass.operator.id}" for ass in assigments],
            message=NewMessageEvent(
                payload=NewMessageEventPayload(
                    conversation_id=conversation.id,
                    new_message=NewMessageSchema(
                        id=message.id,
                        text=message.text,
                        attachments=[],
                        source=message.source,
                        timestamp=message.timestamp,
                        delivery_status=message.delivery_status,
                        sender=MessageSender(
                            id=cast(str, message.external_user_id),
                            name=cast(str, message.external_user_name),
                            sender_type=message.sender_type,
                            avatar_url=conversation.avatar_url,
                        ),
                    ),
                )
            ),
        )

    async def send_to_client(
        self: Self,
        operator: OperatorReadSchema,
        conversation_id: int,
        message_in: MessageInSchema,
    ) -> None:
        conversation = await self.conversation_service.get(conversation_id)
        assigments = await self.assigment_service.get_by_conversation(conversation_id)

        if operator not in [a.operator for a in assigments]:
            raise PermissionException()

        message = await self.message_repository.create(
            MessageCreateSchema(
                sender_type="operator",
                operator_id=operator.id,
                text=message_in.text,
                conversation_id=conversation.id,
                delivery_status="pending",
                source="internal",
            )
        )
        logger.info(
            "Operator {operator_id} created message {message_id}",
            operator_id=operator.id,
            message_id=message.id,
        )
        await self.broker.publish(
            OutgoingMessageSchema(
                internal_id=message.id,
                source=message.source,
                sender=UserSchema(
                    external_id=str(operator.id),
                    name=operator.name,
                    avatar_url=operator.avatar_url,
                ),
                to=UserSchema(
                    external_id=conversation.external_user_id,
                    name=conversation.title,
                    avatar_url=conversation.avatar_url,
                ),
                content=MessageContent(text=message.text, attachments=[]),
                timestamp=message.timestamp,
            ),
            exchange=ChatExchange,
            routing_key=ChatRoutingKeys.outgoing(conversation.channel),
        )

        await self.realtime_transport.broadcast(
            channels=[f"personal:{ass.operator.id}" for ass in assigments],
            message=NewMessageEvent(
                payload=NewMessageEventPayload(
                    conversation_id=conversation.id,
                    client_id=message_in.client_id,
                    new_message=NewMessageSchema(
                        id=message.id,
                        text=message.text,
                        attachments=[],
                        source=message.source,
                        timestamp=message.timestamp,
                        delivery_status=message.delivery_status,
                        sender=MessageSender(
                            id=str(message.operator_id),
                            sender_type=message.sender_type,
                            name=operator.name,
                            avatar_url=operator.avatar_url,
                        ),
                    ),
                )
            ),
        )

    async def update_delivery_status(
        self: Self, message_id: int, delivery_status: DeliveryStatus
    ) -> None:
        message_to_update = await self.message_repository.get(message_id)
        if not message_to_update:
            raise ModuleNotFoundError()

        updated_message = await self.message_repository.update(
            message_to_update.id, MessageUpdateSchema(delivery_status=delivery_status)
        )
        logger.info(
            "Updated message {message_id} changed delivery status from '{before_status}' to '{after_status}'",
            message_id=updated_message.id,
            before_status=message_to_update.delivery_status,
            after_status=updated_message.delivery_status,
        )
        assigments = await self.assigment_service.get_by_conversation(
            updated_message.conversation_id
        )
        await self.realtime_transport.broadcast(
            channels=[f"personal:{ass.operator.id}" for ass in assigments],
            message=DeliveryStatusUpdateEvent(
                payload=DeliveryStatusUpdatePayload(
                    message_id=updated_message.id,
                    delivery_status=updated_message.delivery_status,
                )
            ),
        )

    async def get_by_conversation(
        self: Self, conversation_id: int, cursor: int | None, limit: int = 25
    ) -> Paginated[list[MessageOutSchema]]:
        return await self.message_repository.get_by_conversation(
            conversation_id, cursor=cursor, limit=limit
        )
