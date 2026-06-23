from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class File(Base):
    __tablename__ = "files"

    filename: Mapped[str]
    path: Mapped[str] = mapped_column(unique=True)
    content_type: Mapped[str]
    size: Mapped[int]
