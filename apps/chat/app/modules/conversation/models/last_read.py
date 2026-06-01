from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.schema import UniqueConstraint

from app.database import Base
from app.models import TimestampMixin


class LastRead(Base, TimestampMixin):
    __tablename__ = "last_reads"

    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE")
    )
    operator_id: Mapped[int] = mapped_column(
        ForeignKey("operators.id", ondelete="CASCADE")
    )
    message_id: Mapped[int] = mapped_column(
        ForeignKey("messages.id", ondelete="CASCADE")
    )

    __table_args__ = (
        UniqueConstraint(
            "conversation_id", "operator_id", name="conversation_operator_idx"
        ),
    )
