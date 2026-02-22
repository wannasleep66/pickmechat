from dishka import AsyncContainer
from faststream.asgi.types import ASGIApp

from app.modules.healthcheck.router import health_check_route


def use_routes(container: AsyncContainer) -> list[tuple[str, ASGIApp]]:
    return [("/", health_check_route(container))]
