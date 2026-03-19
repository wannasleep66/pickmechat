import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator, cast

from common.setups.logging import setup_logging
from dishka.integrations.faststream import (
    FastStreamProvider,
)
from dishka.integrations.faststream import (
    setup_dishka as setup_broker_di,
)
from faststream import FastStream
from faststream.asgi import AsgiFastStream
from faststream.rabbit import RabbitBroker
from loguru import logger

from app.consumers import use_consumers
from app.di import make_container
from app.handlers import use_handlers
from app.poller import Poller, PollerProvider
from app.routes import use_routes
from app.settings import AppSettings, EmailSettings


async def setup_poller() -> None:
    """Фабрика Poller приложения"""

    container = make_container(PollerProvider())
    broker = await container.get(RabbitBroker)

    @asynccontextmanager
    async def lifespan(_: Poller) -> AsyncIterator:
        await broker.start()
        yield
        await broker.stop()

    settings = await container.get(EmailSettings)
    poller = Poller(settings=settings, container=container, lifespan=lifespan)
    use_handlers(poller)
    await poller.run()


async def setup_broker() -> None:
    """Фабрика FastStream приложения"""

    container = make_container(FastStreamProvider())
    broker = await container.get(RabbitBroker)
    use_consumers(broker)
    app = AsgiFastStream(broker, asgi_routes=use_routes(container))
    setup_broker_di(container, cast(FastStream, app))
    await app.run(
        log_level=logging.INFO,
        run_extra_options={
            "host": "0.0.0.0",
            "port": 8080,
        },
    )


async def bootstrap() -> None:
    settings = AppSettings()

    setup_logging(env=settings.env)

    apps = [setup_broker(), setup_poller()]

    try:
        await asyncio.gather(*apps)
    except Exception as exc:
        logger.exception("Application is shutdown. Reason: {exc}", exc=str(exc))
