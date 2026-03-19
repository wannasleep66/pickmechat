import sys
from typing import Literal

from loguru import logger

type Env = Literal["prod", "dev"]


def setup_logging(env: Env) -> None:
    logger.remove()

    if env == "dev":
        logger.add(
            sys.stderr,
            level="DEBUG",
            colorize=True,
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{function}</cyan> - <level>{message}</level>",
        )

    if env == "prod":
        logger.add(
            "logs/app.log",
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
            colorize=False,
            serialize=True,
            rotation="100 MB",
            compression="zip",
        )
