from aiogram.dispatcher.router import Router
from aiogram.types import Message
from dishka.integrations.aiogram import inject, FromDishka

from app.modules.message.service import MessageService
from common.schemas.message import MessageContent, MessageSchema
from common.schemas.user import UserSchema


handler = Router()


@handler.message()
@inject
async def handle_incoming(
    message: Message, message_service: FromDishka[MessageService]
) -> None:
    if not message.from_user:
        await message.answer("Не удалось определить кто вы")
        return

    await message_service.send_to_operator(
        MessageSchema(
            id=str(message.message_id),
            source="telegram",
            direction="in",
            content=MessageContent(
                text=message.text if message.text else "", attachments=[]
            ),
            sender=UserSchema(
                external_id=str(message.from_user.id), name=message.from_user.full_name
            ),
            timestamp=str(message.date.timestamp()),
        )
    )
