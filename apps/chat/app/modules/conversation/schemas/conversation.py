from datetime import datetime
from typing import Any, Literal, Self, TypedDict, cast

from common.schemas.message import MessageSource
from pydantic import Field
from pydantic.config import ExtraValues

from app.modules.assigment.model import Assigment
from app.modules.conversation.models.conversation import Conversation
from app.modules.conversation.models.last_read import LastRead
from app.modules.conversation.schemas.last_read import (
    LastReadOutSchema,
    LastReadResponseSchema,
)
from app.modules.message.model import Message
from app.modules.message.schemas import (
    MessageOutSchema,
    MessageResponseSchema,
)
from app.modules.operator.schemas.operator import (
    OperatorOutSchema,
    OperatorResponseSchema,
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


class ConversationOutSchemaModelValidateObj(TypedDict):
    conversation: Conversation
    last_message: Message | None
    last_read: LastRead | None
    unread_count: int


class ConversationOutSchema(ConversationReadSchema):
    last_message: MessageOutSchema | None = None
    last_read: LastReadOutSchema | None = None
    unread_count: int = 0

    @classmethod
    def model_validate(
        cls,
        obj: ConversationOutSchemaModelValidateObj,
        *,
        strict: bool | None = None,
        extra: None | Literal["allow"] | Literal["ignore"] | Literal["forbid"] = None,
        from_attributes: bool | None = None,
        context: Any | None = None,
        by_alias: bool | None = None,
        by_name: bool | None = None,
    ) -> Self:
        conversation = obj["conversation"]
        last_message = obj["last_message"]
        last_read = obj["last_read"]
        unread_count = obj["unread_count"]
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
                last_read=LastReadOutSchema.model_validate(last_read)
                if last_read
                else None,
                unread_count=unread_count,
            ).model_dump(),
            strict=strict,
            extra=extra,
            from_attributes=from_attributes,
            context=context,
            by_alias=by_alias,
            by_name=by_name,
        )


class ConversationAssigmentOutSchema(ReadSchema):
    id: int
    operator: OperatorOutSchema
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    @classmethod
    def model_validate(
        cls,
        obj: Assigment,
        *,
        strict: bool | None = None,
        extra: ExtraValues | None = None,
        from_attributes: bool | None = None,
        context: Any | None = None,
        by_alias: bool | None = None,
        by_name: bool | None = None,
    ) -> Self:
        return super().model_validate(
            cls(
                id=obj.id,
                operator=OperatorOutSchema.model_validate(obj.operator),
                created_at=obj.created_at,
                updated_at=obj.updated_at,
                deleted_at=obj.deleted_at,
            ).model_dump(),
            strict=strict,
            extra=extra,
            from_attributes=from_attributes,
            context=context,
            by_alias=by_alias,
            by_name=by_name,
        )


class ConversationDetailsOutSchema(ConversationOutSchema):
    assigments: list[ConversationAssigmentOutSchema]

    @classmethod
    def model_validate(
        cls: type[Self],
        obj: ConversationOutSchemaModelValidateObj,
        *,
        strict: bool | None = None,
        extra: None | Literal["allow"] | Literal["ignore"] | Literal["forbid"] = None,
        from_attributes: bool | None = None,
        context: Any | None = None,
        by_alias: bool | None = None,
        by_name: bool | None = None,
    ) -> Self:
        conversation = obj["conversation"]
        return super(ConversationOutSchema, cls).model_validate(
            cls(
                **ConversationOutSchema.model_validate(obj).model_dump(),
                assigments=[
                    ConversationAssigmentOutSchema.model_validate(ass)
                    for ass in conversation.assigments
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
    last_read: LastReadResponseSchema | None = None
    unread_count: int = Field(0, description="Количество непрочитанных сообщений")


class ConversationAssigmentResponseSchema(ResponseSchema):
    id: int = Field(..., description="Идентификатор назначения")
    operator: OperatorResponseSchema
    created_at: datetime = Field(..., description="Время создания назначения")
    deleted_at: datetime | None = Field(
        ..., description="Время отзыва назначения с оператора"
    )


class ConversationDetailsResponseSchema(ResponseSchema):
    id: int
    title: str = Field(..., description="Название диалога")
    external_user_id: str = Field(..., description="Внешний ID пользователя")
    channel: MessageSource = Field(
        ..., description="Канал общения (telegram, email, ...)"
    )
    avatar_url: str | None = Field(None, description="URL аватара пользователя")
    closed_at: datetime | None = Field(None, description="Дата закрытия диалога")
    assigments: list[ConversationAssigmentResponseSchema]
    last_message: MessageResponseSchema
    last_read: LastReadResponseSchema | None = None
    unread_count: int = Field(0, description="Количество непрочитанных сообщений")
