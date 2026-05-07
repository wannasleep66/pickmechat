from app.modules.conversation.models.last_read import LastRead
from app.modules.conversation.schemas.last_read import (
    LastReadCreateSchema,
    LastReadReadSchema,
    LastReadUpdateSchema,
)
from app.repositories.database import DatabaseRepository


class LastReadRepository(
    DatabaseRepository[
        LastRead,
        LastReadCreateSchema,
        LastReadReadSchema,
        LastReadUpdateSchema,
    ]
):
    model_type = LastRead
    model_schema = LastReadReadSchema
