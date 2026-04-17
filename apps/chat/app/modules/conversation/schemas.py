from datetime import datetime
from typing import Any, Literal, Self, cast

from common.schemas.message import MessageSource
from pydantic import Field

from app.modules.assigment.schemas import AssigmentOutSchema, AssigmentResponseSchema
from app.modules.conversation.model import Conversation
from app.modules.message.model import Message
from app.modules.message.schemas import (
    MessageOutSchema,
    MessageResponseSchema,
)
from app.schemas.crud import CreateSchema, ReadSchema, UpdateSchema
from app.schemas.request_response import ResponseSchema

ConversationQueryFilter = Literal["assigned", "closed", "open", "all"]


class ConversationReadSchema(ReadSchema):
    title: str
    external_user_id: str
    channel: MessageSource
    avatar_url: str | None = None
    closed_at: datetime | None = None


class ConversationCreateSchema(CreateSchema):
    title: str
    external_user_id: str
    channel: MessageSource
    avatar_url: str | None = None


class ConversationUpdateSchema(UpdateSchema):
    title: str | None = None
    closed_at: datetime | None = None
    avatar_url: str | None = None


class ConversationOutSchema(ConversationReadSchema):
    last_message: MessageOutSchema | None = None

    @classmethod
    def model_validate(
        cls,
        obj: tuple[Conversation, Message | None],
        *,
        strict: bool | None = None,
        extra: None | Literal["allow"] | Literal["ignore"] | Literal["forbid"] = None,
        from_attributes: bool | None = None,
        context: Any | None = None,
        by_alias: bool | None = None,
        by_name: bool | None = None,
    ) -> Self:
        conversation, last_message = obj
        return super().model_validate(
            cls(
                id=conversation.id,
                title=conversation.title,
                external_user_id=conversation.external_user_id,
                channel=cast(MessageSource, conversation.channel),
                avatar_url=conversation.avatar_url,
                closed_at=conversation.closed_at,
                last_message=MessageOutSchema.model_validate(last_message)
                if last_message
                else None,
            ).model_dump(),
            strict=strict,
            extra=extra,
            from_attributes=from_attributes,
            context=context,
            by_alias=by_alias,
            by_name=by_name,
        )


class ConversationDetailsOutSchema(ConversationOutSchema):
    assigments: list[AssigmentOutSchema]

    @classmethod
    def model_validate(
        cls: type[Self],
        obj: tuple[Conversation, Message | None],
        *,
        strict: bool | None = None,
        extra: None | Literal["allow"] | Literal["ignore"] | Literal["forbid"] = None,
        from_attributes: bool | None = None,
        context: Any | None = None,
        by_alias: bool | None = None,
        by_name: bool | None = None,
    ) -> Self:
        return super(ConversationOutSchema, cls).model_validate(
            cls(
                **ConversationOutSchema.model_validate(obj).model_dump(),
                assigments=[
                    AssigmentOutSchema.model_validate(ass) for ass in obj[0].assigments
                ],
            ).model_dump(),
            strict=strict,
            extra=extra,
            from_attributes=from_attributes,
            context=context,
            by_alias=by_alias,
            by_name=by_name,
        )


class ConversationResponseSchema(ResponseSchema):
    id: int
    title: str = Field(..., description="Название диалога")
    external_user_id: str = Field(..., description="Внешний ID пользователя")
    channel: MessageSource = Field(
        ..., description="Канал общения (telegram, email, ...)"
    )
    avatar_url: str | None = Field(None, description="URL аватара пользователя")
    closed_at: datetime | None = Field(None, description="Дата закрытия диалога")
    last_message: MessageResponseSchema


class ConversationDetailsResponseSchema(ResponseSchema):
    id: int
    title: str = Field(..., description="Название диалога")
    external_user_id: str = Field(..., description="Внешний ID пользователя")
    channel: MessageSource = Field(
        ..., description="Канал общения (telegram, email, ...)"
    )
    avatar_url: str | None = Field(None, description="URL аватара пользователя")
    closed_at: datetime | None = Field(None, description="Дата закрытия диалога")
    assigments: list[AssigmentResponseSchema]
    last_message: MessageResponseSchema
