from io import BytesIO
from typing import Self, cast
from uuid import uuid4

from common.schemas.file import FileSchema
from loguru import logger

from app.exceptions import ModelNotFoundException
from app.modules.file.repository import FileRepository
from app.modules.file.schemas import (
    FileCreateSchema,
    FileReadSchema,
    FileStreamSchema,
    UploadFileSchema,
)
from app.repositories.storage import StorageRepository


class FileService:
    def __init__(
        self: Self,
        file_repository: FileRepository,
        storage_repository: StorageRepository,
    ) -> None:
        self.file_repository = file_repository
        self.storage_repository = storage_repository

    async def upload(self: Self, request: UploadFileSchema) -> FileReadSchema:
        filename = request.file.filename if request.file.filename else str(uuid4())[:8]
        path = f"/storage/{request.source}/{filename}"

        async with self.storage_repository:
            await self.storage_repository.write(
                path=path, content=await request.file.read()
            )

        if await self.file_repository.exists_with(path=path):
            replaced = cast(
                FileReadSchema, await self.file_repository.get_by(path=path)
            )
            logger.info(
                "Replaced file {file_id} at {file_path}",
                file_id=replaced.id,
                file_path=replaced.path,
            )
            return replaced

        uploaded = await self.file_repository.create(
            FileCreateSchema(
                filename=filename,
                path=path,
                content_type=cast(str, request.file.content_type),
                size=cast(int, request.file.size),
            )
        )
        logger.info(
            "Uploaded file {file_id} at {file_path}",
            file_id=uploaded.id,
            file_path=uploaded.path,
        )
        return uploaded

    async def download(self: Self, file_id: int) -> FileStreamSchema:
        file = await self.get(file_id)
        async with self.storage_repository:
            stream = BytesIO()
            stream.write(await self.storage_repository.read(file.path))
            stream.seek(0)

        return FileStreamSchema(content=stream, content_type=file.content_type)

    async def delete(self: Self, file_id: int) -> None:
        file_to_delete = await self.get(file_id)

        async with self.storage_repository:
            await self.storage_repository.remove(file_to_delete.path)

        await self.file_repository.delete(file_to_delete.id)
        logger.info("Deleted file {file_id}", file_id=file_to_delete.id)

    async def get(self: Self, file_id: int) -> FileSchema:
        file = await self.file_repository.get(file_id)
        if not file:
            raise ModelNotFoundException()

        return FileSchema(**file.model_dump())
