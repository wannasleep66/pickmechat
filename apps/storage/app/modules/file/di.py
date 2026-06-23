from typing import Self

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.file.repository import FileRepository
from app.modules.file.service import FileService
from app.repositories.storage import StorageRepository


class ModuleProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def file_repository(self: Self, session: AsyncSession) -> FileRepository:
        return FileRepository(session=session)

    @provide(scope=Scope.REQUEST)
    def file_service(
        self: Self,
        file_repository: FileRepository,
        storage_repository: StorageRepository,
    ) -> FileService:
        return FileService(
            file_repository=file_repository, storage_repository=storage_repository
        )
