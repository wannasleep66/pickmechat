from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.modules.rbac.models.role_permission import RolePermission


class Role(Base):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str | None] = mapped_column(default=None)

    permissions_refs: Mapped[list["RolePermission"]] = relationship(
        back_populates="role"
    )
