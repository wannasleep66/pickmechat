from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Path, Query, status

from app.modules.auth.security import OperatorDep
from app.modules.conversation.schemas import (
    ConversationDetailsResponseSchema,
    ConversationQueryFilter,
    ConversationResponseSchema,
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

    conversations = await conversation_service.get_all(operator.id, filter)
    return [ConversationResponseSchema(**c.model_dump()) for c in conversations]


@router.get("/{conversation_id}")
@inject
async def get_conversation_details(
    _: OperatorDep,
    conversation_id: Annotated[int, Path(..., description="Идентификатор диалога")],
    conversation_service: FromDishka[ConversationService],
) -> ConversationDetailsResponseSchema:
    """Получение подробной информации по диалогу"""

    conversation_details = await conversation_service.get_details(conversation_id)
    return ConversationDetailsResponseSchema(**conversation_details.model_dump())


@router.delete("/{conversation_id}/close", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def close_conversation(
    _: OperatorDep,
    conversation_id: Annotated[int, Path(..., description="Идентификатор диалога")],
    conversation_service: FromDishka[ConversationService],
) -> None:
    """Закрыть диалог"""

    await conversation_service.close(conversation_id)
