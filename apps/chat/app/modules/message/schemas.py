from datetime import datetime
from typing import Any, Literal, cast

from common.schemas.message import DeliveryStatus, IncomingMessageSchema, MessageSource
from pydantic import Field
from pydantic.main import BaseModel
from typing_extensions import Self

from app.modules.message.model import Message
from app.schemas.crud import CreateSchema, ReadSchema, UpdateSchema
from app.schemas.request_response import RequestSchema, ResponseSchema

type SenderType = Literal["operator", "user", "system"]


class MessageSender(BaseModel):
    id: str
    sender_type: SenderType
    name: str
    avatar_url: str | None = None


class MessageReadSchema(ReadSchema):
    text: str
    sender_type: SenderType
    operator_id: int | None = None
    external_user_id: str | None = None
    external_user_name: str | None = None
    source: MessageSource
    conversation_id: int
    delivery_status: DeliveryStatus
    timestamp: str


class MessageCreateSchema(CreateSchema):
    text: str
    timestamp: str = Field(default_factory=lambda: str(datetime.now().timestamp()))
    sender_type: SenderType
    operator_id: int | None = None
    external_user_id: str | None = None
    external_user_name: str | None = None
    source: MessageSource
    delivery_status: DeliveryStatus = "pending"
    conversation_id: int


class MessageUpdateSchema(UpdateSchema):
    delivery_status: DeliveryStatus | None = None


class MessageInSchema(BaseModel):
    text: str
    attachments: list[str]
    client_id: str | None = None


class MessageOutSchema(BaseModel):
    id: int
    text: str
    attachments: list[str]
    source: MessageSource
    sender: MessageSender
    delivery_status: DeliveryStatus
    timestamp: str

    @classmethod
    def model_validate(
        cls,
        obj: Message,
        *,
        strict: bool | None = None,
        extra: None | Literal["allow"] | Literal["ignore"] | Literal["forbid"] = None,
        from_attributes: bool | None = None,
        context: Any | None = None,
        by_alias: bool | None = None,
        by_name: bool | None = None,
    ) -> Self:
        sender: MessageSender
        if obj.operator:
            sender = MessageSender(
                id=str(obj.operator.id),
                sender_type=cast(SenderType, obj.sender_type),
                name=obj.operator.name,
                avatar_url=obj.operator.avatar_url,
            )
        else:
            sender = MessageSender(
                id=obj.external_user_id or "system",
                sender_type=cast(SenderType, obj.sender_type),
                name=obj.external_user_name or "System",
                avatar_url=None,
            )

        return super().model_validate(
            MessageOutSchema(
                id=obj.id,
                text=obj.text,
                attachments=[],
                source=cast(MessageSource, obj.source),
                sender=sender,
                delivery_status=cast(DeliveryStatus, obj.delivery_status),
                timestamp=str(obj.timestamp),
            ).model_dump(),
            strict=strict,
            extra=extra,
            from_attributes=from_attributes,
            context=context,
            by_alias=by_alias,
            by_name=by_name,
        )


class MessageRequestSchema(RequestSchema):
    text: str = Field(..., description="Текст сообщения")
    attachments: list[str] = Field(
        default=[], description="Медиа-файлы прикрепленные к сообщению"
    )
    client_id: str | None = Field(
        None,
        description="Клиентский временный идентифактор сообщения, нужен для реализации optimistic update",
    )


class IncomingMessageRequestSchema(RequestSchema, IncomingMessageSchema): ...


class MessageSenderResponseSchema(MessageSender, ResponseSchema): ...


class MessageResponseSchema(ResponseSchema):
    id: int = Field(..., description="Уникальный идентификатор сообщения")
    text: str = Field(..., description="Текст сообщения")
    attachments: list[str] = Field(
        default_factory=list[str], description="Медиа-файлы прикрепленные к сообщению"
    )
    sender: MessageSenderResponseSchema = Field(
        ..., description="Отправитель сообщения"
    )
    source: MessageSource = Field(..., description="Источник отправителя")
    delivery_status: DeliveryStatus = Field(
        ..., description="Статус доставки сообщения"
    )
    timestamp: str = Field(..., description="Время отправки сообщения")
