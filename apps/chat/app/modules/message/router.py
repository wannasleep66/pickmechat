from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Path, Query, status

from app.modules.auth.security import OperatorDep
from app.modules.message.schemas import (
    MessageInSchema,
    MessageRequestSchema,
    MessageResponseSchema,
)
from app.modules.message.service import MessageService

router = APIRouter()


@router.get("/conversations/{conversation_id}/messages")
@inject
async def get_conversation_messages(
    _: OperatorDep,
    conversation_id: Annotated[int, Path(..., description="Идентификатор диалога")],
    message_service: FromDishka[MessageService],
    before_id: int | None = Query(
        None,
        description="Идентификатор сообщения, перед которым нужно получить сообщения",
    ),
    limit: int = Query(25, description="Количество сообщений для получения"),
) -> list[MessageResponseSchema]:
    """Получение сообщений диалога"""

    messages = await message_service.get_by_conversation(
        conversation_id=conversation_id, before_id=before_id, limit=limit
    )
    return [MessageResponseSchema(**message.model_dump()) for message in messages]


@router.post(
    "/conversations/{conversation_id}/messages",
    status_code=status.HTTP_201_CREATED,
)
@inject
async def send_message(
    operator: OperatorDep,
    conversation_id: Annotated[int, Path(..., description="Идентификатор диалога")],
    message_in: MessageRequestSchema,
    message_service: FromDishka[MessageService],
) -> None:
    """Отправка сообщения клиенту"""

    await message_service.send_to_client(
        operator=operator,
        conversation_id=conversation_id,
        message_in=MessageInSchema(**message_in.model_dump()),
    )
