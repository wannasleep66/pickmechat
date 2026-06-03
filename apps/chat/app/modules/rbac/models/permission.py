from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Permission(Base):
    __tablename__ = "permissions"

    resource: Mapped[str] = mapped_column()
    action: Mapped[str] = mapped_column()
    description: Mapped[str | None] = mapped_column()
