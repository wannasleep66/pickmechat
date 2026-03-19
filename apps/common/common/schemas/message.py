from typing import Literal

from pydantic import BaseModel

from common.schemas.user import UserSchema

type MessageSource = Literal["telegram", "email", "internal"]
type MessageDirection = Literal["in", "out"]
type MessageAttachmentType = Literal["file", "image"]

type DeliveryStatus = Literal["delivered", "failed", "pending"]


class MessageAttachment(BaseModel):
    type: MessageAttachmentType
    url: str


class MessageContent(BaseModel):
    text: str
    attachments: list[MessageAttachmentType]


class OutgoingMessageSchema(BaseModel):
    internal_id: int
    source: MessageSource
    sender: UserSchema
    to: UserSchema
    content: MessageContent
    timestamp: str


class IncomingMessageSchema(BaseModel):
    source: MessageSource
    sender: UserSchema
    content: MessageContent
    timestamp: str


class DeliveryStatusSchema(BaseModel):
    internal_message_id: int
    status: DeliveryStatus
