from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Schedule(Base):
    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    medication_id: Mapped[int] = mapped_column(ForeignKey("medications.id"), index=True)
    type: Mapped[str] = mapped_column(String(30))
    time_of_day: Mapped[str] = mapped_column(String(10), default="08:00")
    days_of_week_mask: Mapped[int] = mapped_column(default=0)
    interval_hours: Mapped[int | None] = mapped_column(nullable=True)
    timezone_id: Mapped[str] = mapped_column(String(100), default="UTC")
    grace_minutes: Mapped[int] = mapped_column(default=30)
    is_active: Mapped[bool] = mapped_column(default=True)

    medication = relationship("Medication", back_populates="schedules")
