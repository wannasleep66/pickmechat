from datetime import datetime

from common.schemas.message import IncomingMessageSchema, MessageContent
from common.schemas.user import UserSchema
from dishka import FromDishka

from app.modules.message.service import MessageService
from app.poller import EmailMessage, Router

handler = Router()


@handler.message(subject="Техподдержка")
async def handle_support_message(
    message: EmailMessage, message_service: FromDishka[MessageService]
) -> None:
    await message_service.send_to_operator(
        IncomingMessageSchema(
            source="email",
            sender=UserSchema(
                external_id=message.sender.address, name=message.sender.name
            ),
            content=MessageContent(text=message.content, attachments=[]),
            timestamp=str(datetime.now().timestamp()),
        )
    )
