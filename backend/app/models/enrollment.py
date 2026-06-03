"""
Enrollment model - confirmed student course registrations.
"""

import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import enum


class EnrollmentItemStatus(str, enum.Enum):
    """Enrollment status lifecycle."""
    ENROLLED = "enrolled"
    DROPPED = "dropped"
    WITHDRAWN = "withdrawn"
    COMPLETED = "completed"


class Enrollment(Base):
    """
    Enrollments table - confirmed registrations after approval and payment.
    Tracks student's status in each teaching unit for a semester.
    Status transitions: enrolled → dropped/withdrawn/completed
    """
    __tablename__ = "enrollments"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("students.id"), nullable=False
    )
    teaching_unit_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("teaching_units.id"), nullable=False
    )
    semester_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("semesters.id"), nullable=False
    )
    status: Mapped[EnrollmentItemStatus] = mapped_column(
        SAEnum(EnrollmentItemStatus), default=EnrollmentItemStatus.ENROLLED
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    student: Mapped["Student"] = relationship(
        "Student", back_populates="enrollments"
    )
    teaching_unit: Mapped["TeachingUnit"] = relationship(
        "TeachingUnit", back_populates="enrollments"
    )
    semester: Mapped["Semester"] = relationship(
        "Semester", back_populates="enrollments"
    )
    grade: Mapped["Grade"] = relationship(
        "Grade", back_populates="enrollment", uselist=False
    )
    attendance_records: Mapped[list["Attendance"]] = relationship(
        "Attendance", back_populates="enrollment"
    )

    def __repr__(self) -> str:
        return f"<Enrollment(student={self.student_id}, unit={self.teaching_unit_id}, status={self.status})>"
