import sys
from typing import Literal

from loguru import logger

type Env = Literal["prod", "dev"]


def setup_logging(env: Env) -> None:
    logger.remove()

    if env == "dev":
        logger.add(
            sys.stdout,
            level="DEBUG",
            colorize=True,
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{function}</cyan> - <level>{message}</level>",
        )

    if env == "prod":
        logger.add(
            sys.stdout,
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
            serialize=True,
        )
