from common.schemas.message import MessageAttachmentType

from app.schemas.crud import CreateSchema, ReadSchema, UpdateSchema
from app.schemas.request_response import ResponseSchema


class AttachmentReadSchema(ReadSchema):
    type: MessageAttachmentType
    message_id: int
    file_id: int


class AttachmentCreateSchema(CreateSchema):
    type: MessageAttachmentType
    message_id: int
    file_id: int


class AttachmentUpdateSchema(UpdateSchema): ...


class AttachmentOutSchema(AttachmentReadSchema): ...


class AttachmentResponseSchema(ResponseSchema, AttachmentReadSchema): ...
