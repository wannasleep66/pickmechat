import os
from pathlib import Path
from types import TracebackType
from typing import Self

from aiofiles import open
from aiofiles import os as aos
from pydantic import BaseModel


class LocalStorageParams(BaseModel):
    path: str


class LocalStorageRepository:
    def __init__(self: Self, params: LocalStorageParams) -> None:
        self.work_dir = Path(params.path)
        if not self.work_dir.exists:
            os.makedirs(self.work_dir)

    async def __aenter__(self: Self) -> Self:
        return self

    async def __aexit__(
        self: Self,
        exc_type: type[BaseException] | None = None,
        exc_val: BaseException | None = None,
        exc_tb: TracebackType | None = None,
    ) -> None: ...

    async def read(self: Self, path: str | Path) -> bytes:
        path = self.work_dir / path
        async with open(path, "rb") as stream:
            return await stream.read()

    async def write(self: Self, path: str | Path, content: str | bytes) -> None:
        path = self.work_dir / path
        await aos.makedirs(path.parent, exist_ok=True)
        async with open(path, "wb") as stream:
            await stream.write(
                content.encode("utf-8") if isinstance(content, str) else content
            )

    async def remove(self: Self, path: str | Path) -> None:
        path = self.work_dir / path
        await aos.remove(path)
