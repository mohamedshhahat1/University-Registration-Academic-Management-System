"""
AcademicWarning model - warnings issued to students.
"""

import uuid
from datetime import datetime
from sqlalchemy import Integer, Text, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import enum


class WarningType(str, enum.Enum):
    """Types of academic warnings."""
    GPA_WARNING = "gpa_warning"
    ATTENDANCE_WARNING = "attendance_warning"
    PROBATION = "probation"


class AcademicWarning(Base):
    """
    Academic Warnings table - tracks warnings issued to students.
    GPA warning: CGPA < 2.0
    Attendance warning: attendance < 75%
    Probation: multiple consecutive warnings
    Warning count is tracked for escalation (warning → probation → dismissal).
    """
    __tablename__ = "academic_warnings"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("students.id"), nullable=False
    )
    semester_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("semesters.id"), nullable=False
    )
    type: Mapped[WarningType] = mapped_column(
        SAEnum(WarningType), nullable=False
    )
    reason: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    warning_number: Mapped[int] = mapped_column(
        Integer, default=1, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    # Relationships
    student: Mapped["Student"] = relationship(
        "Student", back_populates="academic_warnings"
    )
    semester = relationship("Semester")

    def __repr__(self) -> str:
        return f"<AcademicWarning(student={self.student_id}, type={self.type}, number={self.warning_number})>"
