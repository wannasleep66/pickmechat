from asyncio import Protocol
from pathlib import Path
from types import TracebackType
from typing import Self


class StorageRepository(Protocol):
    """
    Протокол репозитория файлового хранилища
    """

    async def __aenter__(self) -> Self:
        """
        Вход в контекстный менеджер
        """
        ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_val: BaseException | None = None,
        exc_tb: TracebackType | None = None,
    ) -> None:
        """
        Выход из контекстного менеджера
        """
        ...

    async def read(self: Self, path: str | Path) -> bytes:
        """
        Чтение содержимого файла
        """
        ...

    async def write(self: Self, path: str | Path, content: str | bytes) -> None:
        """
        Создание или переписывание файла
        """
        ...

    async def remove(self: Self, path: str | Path) -> None:
        """
        Удаление файла
        """
        ...
