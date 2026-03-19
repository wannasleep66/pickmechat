from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models import SoftDeleteMixin, TimestampMixin
from app.modules.operator.model import Operator


class Assigment(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "assigments"

    soft_deletable: bool = True

    operator_id: Mapped[int] = mapped_column(
        ForeignKey("operators.id", ondelete="CASCADE")
    )
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE")
    )

    operator: Mapped[Operator] = relationship()

    __table_args__ = (
        UniqueConstraint(
            operator_id, conversation_id, name="operator_conversation_idx"
        ),
    )
