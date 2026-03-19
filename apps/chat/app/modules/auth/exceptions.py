from typing import Self
from app.exceptions import ApplicationException

from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.exception_handlers import http_exception_handler


class InvalidTokenException(ApplicationException):
    @property
    def msg(self: Self) -> str:
        return "Невалидный токен"


class WrongCredentialsException(ApplicationException):
    @property
    def msg(self: Self) -> str:
        return "Неверные учетные данные"


async def wrong_credentials_exception_handler(
    request: Request, exc: WrongCredentialsException
) -> Response:
    return await http_exception_handler(
        request,
        HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=[exc.get_schema().model_dump()],
        ),
    )


async def invalid_token_exception_handler(
    request: Request, exc: InvalidTokenException
) -> Response:
    return await http_exception_handler(
        request,
        HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=[exc.get_schema().model_dump()],
        ),
    )


def use_exception_handlers(app: FastAPI) -> None:
    app.exception_handler(WrongCredentialsException)(
        wrong_credentials_exception_handler
    )
    app.exception_handler(InvalidTokenException)(invalid_token_exception_handler)
