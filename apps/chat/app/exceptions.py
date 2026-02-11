from abc import abstractmethod
from typing import Self

from fastapi import FastAPI, Request, Response, status
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import HTTPException

from app.schemas.exception import ApplicationExceptionSchema, ValidationExceptionSchema


class ApplicationException(Exception):
    """Базовое исключение приложения"""

    @property
    def type(self: Self) -> str:
        return type(self).__name__.replace("Exception", "")

    @property
    @abstractmethod
    def msg(self: Self) -> str: ...

    def get_schema(self: Self) -> ApplicationExceptionSchema:
        return ApplicationExceptionSchema(type=self.type, msg=self.msg)


class ModelNotFoundException(ApplicationException):
    """Исключение не найденного объекта"""

    @property
    def msg(self: Self) -> str:
        return "Модель не найдена"


class ModelAlreadyExistsException(ApplicationException):
    """Исключение уже существующего объекта"""

    @property
    def msg(self: Self) -> str:
        return "Модель уже существует"


class ValidationException(ApplicationException):
    """Исключение валидации"""

    def __init__(self: Self, message: str, field: list[str] | str) -> None:
        super().__init__()
        self.message = message
        self.field = field

    @property
    def fields(self: Self) -> str:
        return ", ".join(self.field) if isinstance(self.field, list) else self.field

    @property
    def msg(self: Self) -> str:
        return self.message

    def get_schema(self: Self) -> ValidationExceptionSchema:
        return ValidationExceptionSchema(
            type=self.type, msg=self.msg, fields=self.fields
        )


async def model_not_found_exception_handler(
    request: Request, exc: ModelNotFoundException
) -> Response:
    return await http_exception_handler(
        request,
        HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[exc.get_schema().model_dump()],
        ),
    )


async def model_already_exists_exception_handler(
    request: Request, exc: ModelAlreadyExistsException
) -> Response:
    return await http_exception_handler(
        request,
        HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=[exc.get_schema().model_dump()],
        ),
    )


async def validation_exception_handler(
    request: Request, exc: ValidationException
) -> Response:
    return await http_exception_handler(
        request,
        HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[exc.get_schema().model_dump()],
        ),
    )


def use_exception_handlers(app: FastAPI) -> None:
    app.exception_handler(ModelNotFoundException)(model_not_found_exception_handler)
    app.exception_handler(ModelAlreadyExistsException)(
        model_already_exists_exception_handler
    )
    app.exception_handler(ValidationException)(validation_exception_handler)
