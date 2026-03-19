from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Path

from app.modules.auth.security import OperatorDep
from app.modules.conversation.schemas import (
    ConversationDetailsResponseSchema,
    ConversationResponseSchema,
)
from app.modules.conversation.service import ConversationService

router = APIRouter(prefix="/conversations")


@router.get("/")
@inject
async def get_all_conversations(
    _: OperatorDep, conversation_service: FromDishka[ConversationService]
) -> list[ConversationResponseSchema]:
    """Получить все диалоги"""

    conversations = await conversation_service.get_all()
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
