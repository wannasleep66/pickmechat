from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.modules.operator.model import Operator


class Message(Base):
    __tablename__ = "messages"

    text: Mapped[str]
    timestamp: Mapped[str]
    sender_type: Mapped[str]
    operator_id: Mapped[int | None] = mapped_column(
        ForeignKey("operators.id", ondelete="SET NULL")
    )
    external_user_id: Mapped[str | None]
    external_user_name: Mapped[str | None]
    source: Mapped[str]
    delivery_status: Mapped[str] = mapped_column(
        default="pending", server_default="pending"
    )
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE")
    )
    operator: Mapped[Operator | None] = relationship(lazy="joined")
