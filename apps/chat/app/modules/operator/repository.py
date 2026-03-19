from app.modules.operator.model import Operator
from app.modules.operator.schemas import (
    OperatorCreateSchema,
    OperatorReadSchema,
    OperatorUpdateSchema,
)
from app.repositories.database import DatabaseRepository


class OperatorRepository(
    DatabaseRepository[
        Operator,
        OperatorCreateSchema,
        OperatorReadSchema,
        OperatorUpdateSchema,
    ]
):
    model_type = Operator
    model_schema = OperatorReadSchema
