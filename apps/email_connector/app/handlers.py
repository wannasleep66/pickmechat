from app.modules.message.handler import handler as message_handler
from app.poller import Poller


def use_handlers(app: Poller) -> None:
    app.include_router(message_handler)
