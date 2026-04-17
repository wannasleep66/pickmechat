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
from app.schemas.pagination import PaginatedResponseSchema

router = APIRouter()


@router.get("/conversations/{conversation_id}/messages")
@inject
async def get_conversation_messages(
    _: OperatorDep,
    conversation_id: Annotated[int, Path(..., description="Идентификатор диалога")],
    message_service: FromDishka[MessageService],
    cursor: int | None = Query(
        None, description="Идентификатор сообщения, после которого нужны сообщения"
    ),
    limit: int = Query(25, description="Количество сообщений для получения"),
) -> PaginatedResponseSchema[list[MessageResponseSchema]]:
    """Получение сообщений диалога"""

    paginated = await message_service.get_by_conversation(
        conversation_id=conversation_id, cursor=cursor, limit=limit
    )

    return PaginatedResponseSchema(
        data=[MessageResponseSchema(**msg.model_dump()) for msg in paginated.data],
        pagination=paginated.pagination,
    )


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
