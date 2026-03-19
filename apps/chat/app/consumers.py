from faststream.rabbit import RabbitBroker

from app.modules.message.consumer import consumer as message_consumer


def use_consumers(broker: RabbitBroker) -> None:
    broker.include_router(message_consumer)
