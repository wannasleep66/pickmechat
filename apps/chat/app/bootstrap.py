from contextlib import asynccontextmanager
from typing import AsyncIterator

from dishka.integrations.fastapi import FastapiProvider, setup_dishka
from fastapi import FastAPI

from app.di import make_container
from app.exceptions import use_exception_handlers
from app.middlewares import use_middlewares
from app.routes import use_routes


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Жизненный цикл приложения"""
    yield


def create_app() -> FastAPI:
    """Фабрика приложения"""

    container = make_container(FastapiProvider())
    app = FastAPI(lifespan=lifespan)
    use_exception_handlers(app)
    use_middlewares(app, allow_origins=["http://localhost:3000"])
    use_routes(app)
    setup_dishka(container, app)
    return app
