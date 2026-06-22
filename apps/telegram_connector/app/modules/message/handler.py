from aiogram.dispatcher.router import Router
from aiogram.types import Message, message_origin_chat
from common.schemas.message import (
    IncomingMessageSchema,
    MessageAttachment,
    MessageAttachmentType,
    MessageContent,
)
from common.schemas.user import UserSchema
from dishka.integrations.aiogram import FromDishka, inject
from loguru import logger

from app.modules.message.service import MessageService

handler = Router()


@handler.message()
@inject
async def handle_incoming(
    message: Message, message_service: FromDishka[MessageService]
) -> None:
    if not message.from_user:
        await message.answer("Не удалось определить кто вы")
        return

    bot = message.bot
    if not bot:
        return

    attachments: list[MessageAttachment] = []

    async def attach(type: MessageAttachmentType, file_id: str):
        file = await bot.get_file(file_id)
        attachments.append(
            MessageAttachment(
                type=type,
                url=f"https://api.telegram.org/file/bot{bot.token}/{file.file_path}",
            )
        )

    if message.photo:
        await attach("image", message.photo[-1].file_id)
    if message.document:
        await attach("file", message.document.file_id)

    logger.info(attachments)

    await message_service.send_to_operator(
        IncomingMessageSchema(
            source="telegram",
            content=MessageContent(
                text=message.text if message.text else "", attachments=attachments
            ),
            sender=UserSchema(
                external_id=str(message.from_user.id), name=message.from_user.full_name
            ),
            timestamp=str(message.date.timestamp()),
        )
    )
