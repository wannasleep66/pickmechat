from typing import Self

import httpx
from loguru import logger

from app.modules.realtime.events import RealtimeEvent
from app.settings import RealtimeTransportSettings


class RealtimeTransport:
    def __init__(self, settings: RealtimeTransportSettings) -> None:
        self.client = httpx.AsyncClient(
            base_url=settings.url,
            headers={
                "content-type": "application/json",
                "X-API-Key": settings.api_key,
                "X-Centrifugo-Error-Mode": "transport",
            },
        )

    async def publish(self: Self, channel: str, message: RealtimeEvent) -> None:
        async with self.client as session:
            try:
                response = await session.post(
                    "/publish",
                    json={
                        "channel": channel,
                        "data": message.model_dump(by_alias=True),
                    },
                )
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                logger.error(
                    "Failed to publish mesage {req} body:{body}",
                    req=exc.request,
                    body=exc.response.json(),
                )
                raise

        logger.info(
            "Published message to channel {channel}: {message}",
            channel=channel,
            message=message,
        )

    async def broadcast(
        self: Self, channels: list[str], message: RealtimeEvent
    ) -> None:
        async with self.client as session:
            try:
                response = await session.post(
                    "/broadcast",
                    json={
                        "channels": channels,
                        "data": message.model_dump(by_alias=True),
                    },
                )
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                logger.error(
                    "Failed to publish mesage {req} body:{body}",
                    req=exc.request,
                    body=exc.response.json(),
                )
                raise

        logger.info(
            "Broadcasted message to channels {channels}: {message}",
            channels=channels,
            message=message,
        )
