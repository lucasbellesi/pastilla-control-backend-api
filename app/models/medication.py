from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Medication(Base):
    __tablename__ = "medications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    dosage_amount: Mapped[str] = mapped_column(String(50))
    dosage_unit: Mapped[str] = mapped_column(String(50))
    notes: Mapped[str | None] = mapped_column(Text(), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)

    owner = relationship("User", back_populates="medications")
    schedules = relationship("Schedule", back_populates="medication", cascade="all, delete-orphan")
