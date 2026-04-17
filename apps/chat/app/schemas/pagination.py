from typing import Literal

from pydantic import BaseModel

from app.schemas.request_response import ResponseSchema

type PaginationType = Literal["pages", "cursor"]


class PagesPaginationMeta(ResponseSchema):
    type: Literal["pages"] = "pages"
    total: bool
    has_next_page: bool
    has_prev_page: bool


class CursorPaginationMeta(ResponseSchema):
    type: Literal["cursor"] = "cursor"
    next_cursor: int | None = None


class Paginated[TData](BaseModel):
    data: TData
    pagination: PagesPaginationMeta | CursorPaginationMeta


class PaginatedResponseSchema[TData](Paginated[TData], ResponseSchema): ...
