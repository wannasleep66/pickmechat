from common.schemas.message import DeliveryStatus
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from pydantic.aliases import AliasGenerator

from app.modules.message.schemas import MessageOutSchema


class RealtimeEventPayload(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(serialization_alias=to_camel)
    )


class RealtimeEvent[RealtimeEventPayload](BaseModel):
    type: str
    payload: RealtimeEventPayload


class NewMessageEventPayload(RealtimeEventPayload):
    conversation_id: int
    client_id: str | None = None
    new_message: MessageOutSchema


class NewMessageEvent(RealtimeEvent):
    type: str = "new_message"
    payload: NewMessageEventPayload


class DeliveryStatusUpdatePayload(RealtimeEventPayload):
    message_id: int
    delivery_status: DeliveryStatus


class DeliveryStatusUpdateEvent(RealtimeEvent):
    type: str = "delivery_status_update"
    payload: DeliveryStatusUpdatePayload


class ConversationAssignedPayload(RealtimeEventPayload):
    conversation_id: int
    operator_id: int


class ConversationUnassignedPayload(RealtimeEventPayload):
    conversation_id: int
    operator_id: int


class ConversationAssigned(RealtimeEvent):
    type: str = "conversation_assigned"
    payload: ConversationAssignedPayload


class ConversationUnassigned(RealtimeEvent):
    type: str = "conversation_unassigned"
    payload: ConversationUnassignedPayload
