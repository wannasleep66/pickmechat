import asyncio
import logging
from typing import cast

from aiogram import Bot, Dispatcher
from common.setups.logging import setup_logging
from dishka.integrations.aiogram import AiogramProvider
from dishka.integrations.aiogram import setup_dishka as setup_bot_di
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
from app.routes import use_routes
from app.settings import AppSettings


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


async def setup_bot() -> None:
    """Фабрика aiogram приложения"""

    container = make_container(AiogramProvider())
    broker = await container.get(RabbitBroker)
    bot = await container.get(Bot)
    dp = Dispatcher()
    use_handlers(dp)
    setup_bot_di(container, dp)

    try:
        logger.info("Starting bot polling")
        await broker.start()
        await dp.start_polling(bot)
    finally:
        await container.close()
        await bot.session.close()
        await broker.stop()


async def bootstrap() -> None:
    settings = AppSettings()

    setup_logging(env=settings.env)

    apps = [setup_broker(), setup_bot()]

    try:
        await asyncio.gather(*apps)
    except Exception as exc:
        logger.exception("Application is shutdown. Reason: {exc}", exc=str(exc))
