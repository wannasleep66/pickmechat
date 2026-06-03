from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.modules.rbac.models.permission import Permission

if TYPE_CHECKING:
    from app.modules.rbac.models.role import Role


class RolePermission(Base):
    __tablename__ = "role_permissions"

    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"),
    )
    permission_id: Mapped[int] = mapped_column(
        ForeignKey("permissions.id", ondelete="CASCADE")
    )

    permission: Mapped[Permission] = relationship()
    role: Mapped["Role"] = relationship(back_populates="permissions_refs")

    __table_args__ = (
        UniqueConstraint(role_id, permission_id, name="role_permissions_idx"),
    )
