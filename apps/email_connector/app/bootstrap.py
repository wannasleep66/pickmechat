import asyncio
import logging

from faststream.asgi import AsgiFastStream
from loguru import logger
from dishka.integrations.faststream import (
    FastStreamProvider,
    setup_dishka as setup_broker_di,
)

from app.routes import use_routes
from app.di import make_container
from app.consumers import RabbitBroker, use_consumers


async def setup_broker() -> None:
    """Фабрика FastStream приложения"""

    container = make_container(FastStreamProvider())
    broker = await container.get(RabbitBroker)
    use_consumers(broker)
    app = AsgiFastStream(broker, asgi_routes=use_routes(container))
    setup_broker_di(container, app)
    await app.run(
        log_level=logging.INFO,
        run_extra_options={
            "host": "0.0.0.0",
            "port": 8080,
        },
    )


async def bootstrap() -> None:
    apps = [setup_broker()]

    try:
        await asyncio.gather(*apps)
    except Exception as exc:
        logger.exception("Application is shutdown. Reason: {exc}", exc=str(exc))
