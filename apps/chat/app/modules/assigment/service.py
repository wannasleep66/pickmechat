from typing import Self

from loguru import logger

from app.exceptions import ModelAlreadyExistsException, ModelNotFoundException
from app.modules.assigment.repository import AssigmentRepository
from app.modules.assigment.schemas import (
    AssigmentCreateSchema,
    AssigmentReadSchema,
)
from app.modules.conversation.schemas.conversation import (
    ConversationAssigmentOutSchema,
)
from app.modules.conversation.service import ConversationService
from app.modules.operator.schemas.operator import OperatorAssigmentOutSchema
from app.modules.operator.service import OperatorService
from app.modules.realtime.events import (
    ConversationAssigned,
    ConversationAssignedPayload,
    ConversationUnassigned,
    ConversationUnassignedPayload,
)
from app.modules.realtime.transport import RealtimeTransport


class AssigmentService:
    def __init__(
        self: Self,
        *,
        assigment_repository: AssigmentRepository,
        operator_service: OperatorService,
        conversation_service: ConversationService,
        realtime_transport: RealtimeTransport,
    ) -> None:
        self.assigment_repository = assigment_repository
        self.operator_service = operator_service
        self.conversation_service = conversation_service
        self.realtime_transport = realtime_transport

    async def assign(
        self: Self, operator_id: int, conversation_id: int
    ) -> AssigmentReadSchema:
        operator_to_assign = await self.operator_service.get(operator_id)
        conversation = await self.conversation_service.get(conversation_id)

        already_existing_assigment = await self.assigment_repository.get_by(
            operator_id=operator_to_assign.id,
            conversation_id=conversation.id,
            with_deleted=True,
        )

        if already_existing_assigment:
            if already_existing_assigment.deleted_at:
                return await self.reassign(already_existing_assigment.id)
            else:
                raise ModelAlreadyExistsException()

        assigned = await self.assigment_repository.create(
            AssigmentCreateSchema(
                operator_id=operator_to_assign.id, conversation_id=conversation.id
            )
        )

        logger.info(
            "Assigned conversation {cid} to operator {oid}",
            cid=assigned.conversation_id,
            oid=assigned.operator_id,
        )

        await self.realtime_transport.publish(
            f"personal:{assigned.operator_id}",
            ConversationAssigned(
                payload=ConversationAssignedPayload(
                    conversation_id=assigned.conversation_id,
                    operator_id=assigned.operator_id,
                )
            ),
        )

        return await self.get(assigned.id)

    async def unassign(self: Self, operator_id: int, conversation_id: int) -> None:
        operator_to_unassign = await self.operator_service.get(operator_id)
        conversation = await self.conversation_service.get(conversation_id)

        assigment_to_delete = await self.assigment_repository.get_by(
            operator_id=operator_to_unassign.id, conversation_id=conversation.id
        )
        if not assigment_to_delete:
            raise ModelNotFoundException()

        await self.assigment_repository.soft_delete(assigment_to_delete.id)

        logger.info(
            "Unassigned conversation {cid} from operator {oid}",
            cid=assigment_to_delete.conversation_id,
            oid=assigment_to_delete.operator_id,
        )

        await self.realtime_transport.publish(
            f"personal:{assigment_to_delete.operator_id}",
            ConversationUnassigned(
                payload=ConversationUnassignedPayload(
                    conversation_id=assigment_to_delete.conversation_id,
                    operator_id=assigment_to_delete.operator_id,
                )
            ),
        )

    async def reassign(self: Self, assigment_id: int) -> AssigmentReadSchema:
        assigment_to_reassign = await self.assigment_repository.get(
            assigment_id, with_deleted=True
        )
        if not assigment_to_reassign:
            raise ModelNotFoundException()

        reassigned = await self.assigment_repository.recover(assigment_to_reassign.id)

        logger.info(
            "Reassigned conversation {cid} to operator {oid}",
            cid=reassigned.conversation_id,
            oid=reassigned.operator_id,
        )

        await self.realtime_transport.publish(
            f"personal:{reassigned.operator_id}",
            ConversationAssigned(
                payload=ConversationAssignedPayload(
                    conversation_id=reassigned.conversation_id,
                    operator_id=reassigned.operator_id,
                )
            ),
        )

        return await self.get(reassigned.id)

    async def get(self: Self, assigment_id: int) -> AssigmentReadSchema:
        assigment = await self.assigment_repository.get(assigment_id)
        if not assigment:
            raise ModelNotFoundException()
        return assigment

    async def get_by_conversation(
        self: Self, conversation_id: int, with_unassigned: bool = False
    ) -> list[ConversationAssigmentOutSchema]:
        return await self.assigment_repository.get_all_by_conversation(
            conversation_id, with_deleted=with_unassigned
        )

    async def get_by_operator(
        self: Self, operator_id: int, with_unassigned: bool = False
    ) -> list[OperatorAssigmentOutSchema]:
        return await self.assigment_repository.get_all_by_operator(
            operator_id, with_deleted=with_unassigned
        )
