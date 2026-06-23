from app.modules.message.models.attachment import Attachment
from app.modules.message.schemas.attachment import (
    AttachmentCreateSchema,
    AttachmentReadSchema,
    AttachmentUpdateSchema,
)
from app.repositories.database import DatabaseRepository


class AttachmentRepository(
    DatabaseRepository[
        Attachment, AttachmentCreateSchema, AttachmentReadSchema, AttachmentUpdateSchema
    ]
):
    model_type = Attachment
    model_schema = AttachmentReadSchema
