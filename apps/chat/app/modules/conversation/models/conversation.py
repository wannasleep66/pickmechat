from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models import TimestampMixin
from app.modules.assigment.model import Assigment


class Conversation(Base, TimestampMixin):
    __tablename__ = "conversations"

    title: Mapped[str]
    external_user_id: Mapped[str] = mapped_column(unique=True)
    avatar_url: Mapped[str | None] = mapped_column(default=None)
    channel: Mapped[str]
    closed_at: Mapped[datetime | None] = mapped_column(default=None)

    assigments: Mapped[list[Assigment]] = relationship()
