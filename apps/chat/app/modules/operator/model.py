from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Operator(Base):
    __tablename__ = "operators"

    username: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str]
    name: Mapped[str]
    avatar_url: Mapped[str | None]
