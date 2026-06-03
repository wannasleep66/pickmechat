from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.modules.rbac.models.role import Role


class OperatorRole(Base):
    __tablename__ = "operator_roles"

    operator_id: Mapped[int] = mapped_column(
        ForeignKey("operators.id", ondelete="CASCADE")
    )
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"),
    )

    role: Mapped[Role] = relationship()

    __table_args__ = (
        UniqueConstraint(operator_id, role_id, name="operator_roles_idx"),
    )
