from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.modules.operator.models.availability_status import AvailabilityStatus

if TYPE_CHECKING:
    from app.modules.assigment.model import Assigment
    from app.modules.rbac.models.operator_role import OperatorRole


class Operator(Base):
    __tablename__ = "operators"

    username: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str]
    name: Mapped[str]
    avatar_url: Mapped[str | None]

    status: Mapped[AvailabilityStatus | None] = relationship(lazy="joined")
    assigments: Mapped[list["Assigment"]] = relationship()
    roles_refs: Mapped[list["OperatorRole"]] = relationship()
