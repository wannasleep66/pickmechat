from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Query, UploadFile, status

from app.modules.file.schemas import (
    FileResponseSchema,
    FileStreamResponse,
    UploadFileSchema,
)
from app.modules.file.service import FileService

router = APIRouter()


@router.get("/{file_id}")
@inject
async def download_file(
    file_id: int, file_service: FromDishka[FileService]
) -> FileStreamResponse:
    """
    Получить файл по id
    """

    file = await file_service.download(file_id)
    return FileStreamResponse(content=file.content, media_type=file.content_type)


@router.post("/upload", status_code=status.HTTP_201_CREATED)
@inject
async def upload_file(
    source: Annotated[str, Query()],
    file: UploadFile,
    file_service: FromDishka[FileService],
) -> FileResponseSchema:
    """
    Загрузка файла
    """

    uploaded = await file_service.upload(UploadFileSchema(source=source, file=file))
    return FileResponseSchema(**uploaded.model_dump())


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_file(file_id: int, file_service: FromDishka[FileService]) -> None:
    """
    Удаление файла
    """

    await file_service.delete(file_id)
