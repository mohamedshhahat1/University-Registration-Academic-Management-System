"""
SemesterGPA model - calculated GPA per student per semester.
"""

import uuid
from datetime import datetime
from sqlalchemy import Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class SemesterGPA(Base):
    """
    Semester GPAs table - stores calculated GPA for each student per semester.
    Used for GPA history and CGPA calculation.
    GPA = total_points / total_hours
    """
    __tablename__ = "semester_gpas"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("students.id"), nullable=False
    )
    semester_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("semesters.id"), nullable=False
    )
    gpa: Mapped[float] = mapped_column(
        Numeric(3, 2), nullable=False
    )
    total_hours: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    total_points: Mapped[float] = mapped_column(
        Numeric(7, 2), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    # Relationships
    student: Mapped["Student"] = relationship(
        "Student", back_populates="semester_gpas"
    )
    semester: Mapped["Semester"] = relationship(
        "Semester", back_populates="semester_gpas"
    )

    def __repr__(self) -> str:
        return f"<SemesterGPA(student={self.student_id}, gpa={self.gpa})>"
