from typing import BinaryIO, Self

import httpx
from common.schemas.file import FileSchema
from loguru import logger

from app.modules.storage.schemas import StreamingResponse


class StorageGateway:
    def __init__(self: Self, url: str) -> None:
        self.url = url

    async def upload(
        self: Self, filename: str, content: BinaryIO, content_type: str
    ) -> FileSchema:
        async with httpx.AsyncClient(base_url=self.url) as session:
            try:
                response = await session.post(
                    url="/upload",
                    params={"source": "telegram"},
                    files={"file": (filename, content, content_type)},
                )
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                logger.error(
                    "Failed to publish mesage {req} body:{body}",
                    req=exc.request,
                    body=exc.response.json(),
                )
                raise

            return FileSchema.model_validate(response.json(), by_alias=True)

    async def download(self: Self, file_id: int) -> StreamingResponse:
        async with httpx.AsyncClient(base_url=self.url) as session:
            try:
                response = await session.get(
                    url=f"/{file_id}",
                )
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                logger.error(
                    "Failed to publish mesage {req} body:{body}",
                    req=exc.request,
                    body=exc.response.json(),
                )
                raise
            return StreamingResponse(
                content=response.content,
                content_type=response.headers.get("content-type"),
            )

    async def get(self: Self, file_id: int) -> FileSchema:
        async with httpx.AsyncClient(base_url=self.url) as session:
            try:
                response = await session.get(
                    url=f"/{file_id}/meta",
                )
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                logger.error(
                    "Failed to publish mesage {req} body:{body}",
                    req=exc.request,
                    body=exc.response.json(),
                )
                raise
            return FileSchema.model_validate(response.json(), by_alias=True)
