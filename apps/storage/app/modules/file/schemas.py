from common.schemas.file import FileSchema
from fastapi import UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict
from starlette.responses import ContentStream

from app.schemas.crud import CreateSchema, ReadSchema, UpdateSchema
from app.schemas.request_response import ResponseSchema


class FileReadSchema(ReadSchema):
    filename: str
    path: str
    content_type: str
    size: int


class FileCreateSchema(CreateSchema):
    filename: str
    path: str
    content_type: str
    size: int


class FileUpdateSchema(UpdateSchema): ...


class UploadFileSchema(BaseModel):
    source: str
    file: UploadFile


class FileResponseSchema(ResponseSchema, FileSchema): ...


class FileStreamSchema(BaseModel):
    content: ContentStream
    content_type: str

    model_config = ConfigDict(arbitrary_types_allowed=True)


class FileStreamResponse(StreamingResponse): ...
