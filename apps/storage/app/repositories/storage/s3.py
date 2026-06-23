from pathlib import Path
from types import TracebackType
from typing import TYPE_CHECKING, Self

import aiobotocore
import aiobotocore.session
from aiobotocore.client import AioBaseClient
from aiobotocore.session import AioSession
from pydantic import BaseModel

if TYPE_CHECKING:
    from types_aiobotocore_s3.client import S3Client as AioBaseClient
else:
    from aiobotocore.client import AioBaseClient


class S3StorageParams(BaseModel):
    endpoint: str
    aws_secret_access_key: str
    aws_access_key_id: str
    port: int
    bucket: str
    secure: bool = False
    region_name: str = "us-east-1"


class S3StorageRepository:
    def __init__(self: Self, params: S3StorageParams) -> None:
        self.params = params
        self.bucket = self.params.bucket

        self.session: AioSession | None = None
        self.client: AioBaseClient | None = None

        self.endpoint = f"http://{self.params.endpoint}:{self.params.port}"

    async def __aenter__(self: Self) -> Self:
        self.session = aiobotocore.session.get_session()
        self.client = await self.session.create_client(  # pyright: ignore
            "s3",
            endpoint_url=self.endpoint,
            aws_access_key_id=self.params.aws_access_key_id,
            aws_secret_access_key=self.params.aws_secret_access_key,
            region_name=self.params.region_name,
        ).__aenter__()
        return self

    async def __aexit__(
        self: Self,
        exc_type: type[BaseException] | None = None,
        exc_val: BaseException | None = None,
        exc_tb: TracebackType | None = None,
    ) -> None:
        if not self.client:
            return

        await self.client.__aexit__(exc_type, exc_val, exc_tb)
        self.client = None
        self.session = None

    async def read(self: Self, path: str | Path) -> bytes:
        assert self.client
        key = self.get_str_path(path)
        response = await self.client.get_object(Bucket=self.bucket, Key=key)
        async with response["Body"] as stream:
            return await stream.read()

    async def write(self: Self, path: str | Path, content: str | bytes) -> None:
        assert self.client
        key = self.get_str_path(path)
        content = content.encode("utf-8") if isinstance(content, str) else content
        await self.client.put_object(Bucket=self.params.bucket, Key=key, Body=content)

    async def remove(self: Self, path: str | Path) -> None:
        assert self.client
        key = self.get_str_path(path)
        await self.client.delete_object(Bucket=self.params.bucket, Key=key)

    @staticmethod
    def get_str_path(path: str | Path) -> str:
        if isinstance(path, Path):
            return "" if path == Path("") else str(path)
        return path
