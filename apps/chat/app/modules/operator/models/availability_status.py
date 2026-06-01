from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models import UpdatedAtMixin


class AvailabilityStatus(Base, UpdatedAtMixin):
    __tablename__ = "availability_statuses"

    status: Mapped[str]
    operator_id: Mapped[int] = mapped_column(
        ForeignKey("operators.id", ondelete="CASCADE"), unique=True
    )
