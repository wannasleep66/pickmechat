from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Attachment(Base):
    __tablename__ = "attachments"

    type: Mapped[str]
    message_id: Mapped[int] = mapped_column(
        ForeignKey("messages.id", ondelete="CASCADE")
    )
    file_id: Mapped[int] = mapped_column()
    filename: Mapped[str] = mapped_column()
    size: Mapped[int] = mapped_column()
