from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Path, status

from app.modules.assigment.service import AssigmentService
from app.modules.auth.security import OperatorDep

router = APIRouter()


@router.post(
    "/conversations/{conversation_id}/operators/{operator_id}/assign",
    status_code=status.HTTP_201_CREATED,
)
@inject
async def assign_conversation_to_operator(
    _: OperatorDep,
    conversation_id: Annotated[int, Path(..., description="Идентификатор диалога")],
    operator_id: Annotated[int, Path(..., description="Идентификатор оператора")],
    assigment_service: FromDishka[AssigmentService],
) -> None:
    """Назначение диалога оператору"""

    await assigment_service.assign(operator_id, conversation_id)


@router.delete(
    "/conversations/{conversation_id}/operators/{operator_id}/assign",
    status_code=status.HTTP_204_NO_CONTENT,
)
@inject
async def unassign_conversation_from_operator(
    _: OperatorDep,
    conversation_id: Annotated[int, Path(..., description="Идентификатор диалога")],
    operator_id: Annotated[int, Path(..., description="Идентификатор оператора")],
    assigment_service: FromDishka[AssigmentService],
) -> None:
    """Отзыв диалога от оператора"""

    await assigment_service.unassign(operator_id, conversation_id)


@router.post(
    "/conversations/{conversation_id}/take", status_code=status.HTTP_201_CREATED
)
@inject
async def take_conversation(
    operator: OperatorDep,
    conversation_id: Annotated[int, Path(..., description="Идентификатор диалога")],
    assigment_service: FromDishka[AssigmentService],
) -> None:
    """Назначение диалога себе"""

    await assigment_service.assign(operator.id, conversation_id)
