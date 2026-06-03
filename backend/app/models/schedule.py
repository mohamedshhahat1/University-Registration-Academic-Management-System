"""
Schedule model - time slots for teaching units.
"""

import uuid
from datetime import datetime, time
from sqlalchemy import Time, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import enum


class DayOfWeek(str, enum.Enum):
    """Days of the academic week."""
    SUNDAY = "sunday"
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"


class Schedule(Base):
    """
    Schedules table - defines when and where a teaching unit meets.
    Used for conflict detection during registration.
    A teaching unit can have multiple schedule entries (e.g., meets twice a week).
    """
    __tablename__ = "schedules"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    teaching_unit_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("teaching_units.id"), nullable=False
    )
    day_of_week: Mapped[DayOfWeek] = mapped_column(
        SAEnum(DayOfWeek), nullable=False
    )
    start_time: Mapped[time] = mapped_column(
        Time, nullable=False
    )
    end_time: Mapped[time] = mapped_column(
        Time, nullable=False
    )
    classroom_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("classrooms.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    # Relationships
    teaching_unit: Mapped["TeachingUnit"] = relationship(
        "TeachingUnit", back_populates="schedules"
    )
    classroom: Mapped["Classroom"] = relationship(
        "Classroom", back_populates="schedules"
    )

    def __repr__(self) -> str:
        return f"<Schedule(unit={self.teaching_unit_id}, day={self.day_of_week}, {self.start_time}-{self.end_time})>"
