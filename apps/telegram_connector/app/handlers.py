from aiogram import Dispatcher

from app.modules.message.handler import handler as message_handler


def use_handlers(dp: Dispatcher) -> None:
    dp.include_router(message_handler)
