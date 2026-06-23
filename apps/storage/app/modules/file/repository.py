from app.modules.file.model import File
from app.modules.file.schemas import FileCreateSchema, FileReadSchema, FileUpdateSchema
from app.repositories.database import DatabaseRepository


class FileRepository(
    DatabaseRepository[File, FileCreateSchema, FileReadSchema, FileUpdateSchema]
):
    model_type = File
    model_schema = FileReadSchema
