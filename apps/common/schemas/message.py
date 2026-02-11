from typing import Literal

from pydantic import BaseModel

from schemas.user import UserSchema

type MessageSource = Literal["telegram", "whatsup", "internal"]
type MessageDirection = Literal["in", "out"]
type MessageAttachmentType = Literal["file", "image"]


class MessageAttachment(BaseModel):
    type: MessageAttachmentType
    url: str


class MessageContent(BaseModel):
    text: str
    attachments: list[MessageAttachmentType]


class MessageSchema(BaseModel):
    id: str
    source: MessageSource
    direction: MessageDirection
    sender: UserSchema
    timestamp: str
