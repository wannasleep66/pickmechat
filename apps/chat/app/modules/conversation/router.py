from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Path, Query, status

from app.modules.auth.security import OperatorDep, auth
from app.modules.conversation.schemas.conversation import (
    ConversationDetailsResponseSchema,
    ConversationQueryFilter,
    ConversationResponseSchema,
)
from app.modules.conversation.schemas.last_read import (
    LastReadInSchema,
    LastReadRequestSchema,
)
from app.modules.conversation.service import ConversationService

router = APIRouter(prefix="/conversations")


@router.get("/")
@inject
async def get_all_conversations(
    operator: OperatorDep,
    conversation_service: FromDishka[ConversationService],
    filter: ConversationQueryFilter = Query("all"),
) -> list[ConversationResponseSchema]:
    """Получить все диалоги"""

    conversations = await conversation_service.get_all(operator, filter)
    return [ConversationResponseSchema(**c.model_dump()) for c in conversations]


@router.get("/{conversation_id}")
@inject
async def get_conversation_details(
    operator: OperatorDep,
    conversation_id: Annotated[int, Path(..., description="Идентификатор диалога")],
    conversation_service: FromDishka[ConversationService],
) -> ConversationDetailsResponseSchema:
    """Получение подробной информации по диалогу"""

    conversation_details = await conversation_service.get_details(
        operator, conversation_id
    )
    return ConversationDetailsResponseSchema(**conversation_details.model_dump())


@router.post("/{conversation_id}/last_read", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def set_conversation_last_read(
    operator: OperatorDep,
    conversation_id: Annotated[int, Path(..., description="Идентификатор диалога")],
    last_read_in: LastReadRequestSchema,
    conversation_service: FromDishka[ConversationService],
) -> None:
    """Установка последнего прочитанного сообщения в диалоге"""

    await conversation_service.set_last_read(
        operator,
        last_read_in=LastReadInSchema(
            **last_read_in.model_dump(), conversation_id=conversation_id
        ),
    )


@router.delete(
    "/{conversation_id}/close",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[auth()],
)
@inject
async def close_conversation(
    conversation_id: Annotated[int, Path(..., description="Идентификатор диалога")],
    conversation_service: FromDishka[ConversationService],
) -> None:
    """Закрыть диалог"""

    await conversation_service.close(conversation_id)
