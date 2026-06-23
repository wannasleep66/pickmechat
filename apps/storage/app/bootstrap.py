import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from common.setups.logging import setup_logging
from dishka.integrations.fastapi import FastapiProvider
from dishka.integrations.fastapi import setup_dishka as setup_web_di
from fastapi import FastAPI
from loguru import logger
from uvicorn import Config, Server

from app.di import make_container
from app.exceptions import use_exception_handlers
from app.middlewares import use_middlewares
from app.monitoring import use_monitoring
from app.routes import use_routes
from app.settings import AppSettings


async def setup_web() -> None:
    container = make_container(FastapiProvider())

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
        """Жизненный цикл приложения"""
        yield

    app = FastAPI(lifespan=lifespan)
    use_exception_handlers(app)
    use_middlewares(app, ["*", "http://localhost:5173"])
    use_monitoring(app, app_name="pickmestorage")
    use_routes(app)
    setup_web_di(container, app)
    await Server(Config(app=app, host="0.0.0.0", port=8080)).serve()


async def bootstrap() -> None:
    settings = AppSettings()

    setup_logging(settings.env)

    apps = [setup_web()]

    try:
        await asyncio.gather(*apps)
    except Exception as exc:
        logger.exception("Application is shutdown. Reason: {exc}", exc=str(exc))
