from dishka import AsyncContainer
from faststream.asgi.types import ASGIApp
from prometheus_client import CollectorRegistry, make_asgi_app


async def use_monitoring(container: AsyncContainer) -> list[tuple[str, ASGIApp]]:
    monitoring_registry = await container.get(CollectorRegistry)
    return [("/metrics", make_asgi_app(monitoring_registry))]
