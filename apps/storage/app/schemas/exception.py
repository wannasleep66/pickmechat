from pydantic import BaseModel


class ApplicationExceptionSchema(BaseModel):
    """Базовое исключение приложения"""

    type: str
    msg: str


class ValidationExceptionSchema(ApplicationExceptionSchema):
    """Ошибка валидации"""

    fields: str
