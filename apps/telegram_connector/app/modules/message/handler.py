from aiogram.dispatcher.router import Router
from aiogram.types import Message
from common.schemas.message import IncomingMessageSchema, MessageContent
from common.schemas.user import UserSchema
from dishka.integrations.aiogram import FromDishka, inject

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

    await message_service.send_to_operator(
        IncomingMessageSchema(
            source="telegram",
            content=MessageContent(
                text=message.text if message.text else "", attachments=[]
            ),
            sender=UserSchema(
                external_id=str(message.from_user.id), name=message.from_user.full_name
            ),
            timestamp=str(message.date.timestamp()),
        )
    )
