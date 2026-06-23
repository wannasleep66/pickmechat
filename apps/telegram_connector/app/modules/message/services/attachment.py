from io import BytesIO
from typing import Self

from aiogram import Bot
from common.schemas.message import MessageAttachment, MessageAttachmentType

from app.modules.storage.gateway import StorageGateway


class AttachmentService:
    def __init__(self: Self, bot: Bot, storage_gateway: StorageGateway) -> None:
        self.bot = bot
        self.storage_gateway = storage_gateway

    async def upload(
        self: Self, type: MessageAttachmentType, file_id: str, content_type: str
    ) -> MessageAttachment:
        file = await self.bot.get_file(file_id)
        content = BytesIO()
        await self.bot.download(file=file, destination=content)
        uploaded = await self.storage_gateway.upload(
            file.file_id, content, content_type
        )
        return MessageAttachment(
            type=type,
            id=uploaded.id,
        )
