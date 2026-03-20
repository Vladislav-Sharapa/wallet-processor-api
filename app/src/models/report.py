from datetime import datetime

from app.src.core.models import BaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from app.src.models.user import User
from app.src.schemas.report import ReportStatus


class Report(BaseModel):
    __tablename__ = "report"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    task_id: Mapped[str] = mapped_column(nullable=True)
    start_date: Mapped[datetime] = mapped_column(nullable=False)
    end_date: Mapped[datetime] = mapped_column(nullable=False)

    report_name: Mapped[str] = mapped_column(nullable=True)
    status: Mapped[ReportStatus] = mapped_column(
        nullable=True, default=ReportStatus.PENDING
    )

    owner: Mapped[User] = relationship("User", back_populates="report")
