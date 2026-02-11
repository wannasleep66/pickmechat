from pydantic import BaseModel, ConfigDict


class ReadSchema(BaseModel):
    """
    Схема для чтения данных
    """

    id: int

    model_config = ConfigDict(from_attributes=True)


class CreateSchema(BaseModel):
    """
    Схема для создания данных
    """

    ...


class UpdateSchema(BaseModel):
    """
    Схема для обновления данных
    """

    ...
