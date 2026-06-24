from aiogram.dispatcher.router import Router
from aiogram.types import Message
from common.schemas.message import (
    IncomingMessageSchema,
    MessageContent,
)
from common.schemas.user import UserSchema
from dishka.integrations.aiogram import FromDishka, inject

from app.modules.message.services.attachment import (
    AttachmentService,
)
from app.modules.message.services.message import MessageService

handler = Router()


@handler.message()
@inject
async def handle_incoming(
    message: Message,
    message_service: FromDishka[MessageService],
    attachment_service: FromDishka[AttachmentService],
) -> None:
    if not message.from_user:
        await message.answer("Не удалось определить кто вы")
        return

    bot = message.bot
    if not bot:
        return

    files = []
    if message.photo:
        photo = message.photo[-1]
        files.append(("image", photo.file_id, "image/png"))

    if message.document:
        document = message.document
        files.append(
            ("file", document.file_id, document.mime_type or "application/octet-stream")
        )

    attachments = [await attachment_service.upload(*file) for file in files]

    await message_service.send_to_operator(
        IncomingMessageSchema(
            source="telegram",
            content=MessageContent(
                text=message.text or message.caption or "", attachments=attachments
            ),
            sender=UserSchema(
                external_id=str(message.from_user.id), name=message.from_user.full_name
            ),
            timestamp=str(message.date.timestamp()),
        )
    )
