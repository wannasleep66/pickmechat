import asyncio
from typing import Self

from aiogram import Bot
from aiogram.types import BufferedInputFile
from common.constants.rabbitmq import ChatExchange, ChatRoutingKeys
from common.schemas.file import FileSchema
from common.schemas.message import IncomingMessageSchema, OutgoingMessageSchema
from faststream.rabbit.annotations import RabbitBroker
from loguru import logger

from app.modules.storage.gateway import StorageGateway
from apps.telegram_connector.app.modules.storage.schemas import StreamingResponse


class MessageService:
    def __init__(
        self: Self, *, bot: Bot, broker: RabbitBroker, storage_gateway: StorageGateway
    ) -> None:
        self.bot = bot
        self.broker = broker
        self.storage_gateway = storage_gateway

    async def send_to_client(self: Self, message: OutgoingMessageSchema) -> None:
        if message.content.attachments:

            async def upload(file_id) -> tuple[FileSchema, StreamingResponse]:
                meta, file = await asyncio.gather(
                    *[
                        self.storage_gateway.get(file_id),
                        self.storage_gateway.download(file_id),
                    ]
                )
                return (meta, file)

            uploaded = await asyncio.gather(
                *[upload(attachment.id) for attachment in message.content.attachments]
            )

            for meta, file in uploaded:
                if file.content_type.startswith("image/"):
                    await self.bot.send_photo(
                        chat_id=message.to.external_id,
                        photo=BufferedInputFile(file.content, filename=meta.filename),
                    )
                    continue

                await self.bot.send_document(
                    chat_id=message.to.external_id,
                    document=BufferedInputFile(file.content, filename=meta.filename),
                )

        if message.content.text:
            await self.bot.send_message(
                chat_id=message.to.external_id,
                text=message.content.text,
            )

        logger.info(
            "Sent message to user {user_id} from operator {operator_id}",
            user_id=message.to.external_id,
            operator_id=message.sender.external_id,
        )

    async def send_to_operator(self: Self, message: IncomingMessageSchema) -> None:
        await self.broker.publish(
            message.model_dump(),
            exchange=ChatExchange,
            routing_key=ChatRoutingKeys.incoming("telegram"),
        )
        logger.info(
            "Sent message to operator from user {user_id}",
            user_id=message.sender.external_id,
        )
