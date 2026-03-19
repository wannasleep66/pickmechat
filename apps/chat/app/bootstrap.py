import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator

from common.setups.logging import setup_logging
from dishka.integrations.fastapi import FastapiProvider
from dishka.integrations.fastapi import setup_dishka as setup_web_di
from dishka.integrations.faststream import (
    FastStreamProvider,
)
from dishka.integrations.faststream import (
    setup_dishka as setup_broker_di,
)
from fastapi import FastAPI
from faststream import FastStream
from faststream.rabbit import RabbitBroker
from loguru import logger
from uvicorn import Config, Server

from app.consumers import use_consumers
from app.di import make_container
from app.exceptions import use_exception_handlers
from app.middlewares import use_middlewares
from app.modules.auth.exceptions import (
    use_exception_handlers as use_auth_exception_handlers,
)
from app.routes import use_routes
from app.settings import AppSettings


async def setup_broker() -> None:
    container = make_container(FastStreamProvider())
    broker = await container.get(RabbitBroker)
    use_consumers(broker)
    app = FastStream(broker)
    setup_broker_di(container, app)
    await app.run()


async def setup_web() -> None:
    """Фабрика приложения"""

    container = make_container(FastapiProvider())
    broker = await container.get(RabbitBroker)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        """Жизненный цикл приложения"""

        await broker.start()
        yield
        await broker.stop()

    app = FastAPI(lifespan=lifespan)
    use_exception_handlers(app)
    use_auth_exception_handlers(app)
    use_middlewares(app, allow_origins=["*", "http://localhost:5173"])
    use_routes(app)
    setup_web_di(container, app)
    await Server(Config(app=app, host="0.0.0.0", port=8080)).serve()


async def bootstrap() -> None:
    settings = AppSettings()

    setup_logging(env=settings.env)

    apps = [setup_broker(), setup_web()]

    try:
        await asyncio.gather(*apps)
    except Exception as exc:
        logger.exception("Application is shutdown. Reason: {exc}", exc=str(exc))
