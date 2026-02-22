from faststream.asgi import AsgiResponse, get
from faststream.asgi.types import ASGIApp, Scope
from dishka import AsyncContainer
from faststream.rabbit import RabbitBroker
from loguru import logger

from app.modules.healthcheck.schemas import HealthCheckResponseSchema


def health_check_route(container: AsyncContainer) -> ASGIApp:

    async def ensure_rabbitmq_is_healthy() -> None:
        broker = await container.get(RabbitBroker)
        await broker.ping(timeout=5.0)

    @get
    async def func(_: Scope) -> AsgiResponse:
        healthy_response = AsgiResponse(
            HealthCheckResponseSchema(status="working").model_dump_json().encode(),
            status_code=200,
        )
        unhealthy_response = AsgiResponse(
            HealthCheckResponseSchema(status="error").model_dump_json().encode(),
            status_code=500,
        )

        try:
            await ensure_rabbitmq_is_healthy()
        except Exception as exc:
            logger.error(str(exc))
            return unhealthy_response

        return healthy_response

    return func
