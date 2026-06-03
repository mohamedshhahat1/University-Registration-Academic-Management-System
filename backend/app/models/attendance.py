"""
Attendance model - tracking student presence in classes.
"""

import uuid
from datetime import datetime, date
from sqlalchemy import Text, Date, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import enum


class AttendanceStatus(str, enum.Enum):
    """Attendance record status."""
    PRESENT = "present"
    ABSENT = "absent"
    EXCUSED = "excused"


class Attendance(Base):
    """
    Attendance table - daily attendance records per enrollment.
    Used to calculate attendance percentage and generate warnings.
    Warning triggered when attendance drops below 75%.
    """
    __tablename__ = "attendance"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    enrollment_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("enrollments.id"), nullable=False
    )
    teaching_unit_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("teaching_units.id"), nullable=False
    )
    date: Mapped[date] = mapped_column(
        Date, nullable=False
    )
    status: Mapped[AttendanceStatus] = mapped_column(
        SAEnum(AttendanceStatus), nullable=False
    )
    notes: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    # Relationships
    enrollment: Mapped["Enrollment"] = relationship(
        "Enrollment", back_populates="attendance_records"
    )
    teaching_unit: Mapped["TeachingUnit"] = relationship("TeachingUnit")

    def __repr__(self) -> str:
        return f"<Attendance(enrollment={self.enrollment_id}, date={self.date}, status={self.status})>"
