from typing import BinaryIO, Self

import httpx
from common.schemas.file import FileSchema
from loguru import logger


class StorageGateway:
    def __init__(self: Self, url: str) -> None:
        self.client = httpx.AsyncClient(base_url=url)

    async def upload(
        self: Self, filename: str, content: BinaryIO, content_type: str
    ) -> FileSchema:
        async with self.client as session:
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
