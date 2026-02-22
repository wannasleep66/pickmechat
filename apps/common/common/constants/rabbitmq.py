from faststream.rabbit import ExchangeType, RabbitExchange

ChatExchange = RabbitExchange("chat.topic", type=ExchangeType.TOPIC)


class ChatRoutingKeys:
    @staticmethod
    def incoming(source: str) -> str:
        return f"incoming.message.{source}"

    @staticmethod
    def outgoing(source: str) -> str:
        return f"outgoing.message.{source}"

    @staticmethod
    def all_incoming() -> str:
        return "incoming.message.*"
