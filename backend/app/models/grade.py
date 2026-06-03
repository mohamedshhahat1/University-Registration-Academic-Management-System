"""
Grade model - student grades for enrolled courses.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Grade(Base):
    """
    Grades table - stores grade components and final results.
    Components: Midterm 1 (30%), Midterm 2 (20%), Coursework (10%), Final (40%)
    Automatically calculates total_score, letter_grade, and grade_points.
    """
    __tablename__ = "grades"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    enrollment_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("enrollments.id"), unique=True, nullable=False
    )
    midterm1: Mapped[float | None] = mapped_column(
        Numeric(5, 2), nullable=True  # Out of 100, weighted 30%
    )
    midterm2: Mapped[float | None] = mapped_column(
        Numeric(5, 2), nullable=True  # Out of 100, weighted 20%
    )
    coursework: Mapped[float | None] = mapped_column(
        Numeric(5, 2), nullable=True  # Out of 100, weighted 10%
    )
    final_exam: Mapped[float | None] = mapped_column(
        Numeric(5, 2), nullable=True  # Out of 100, weighted 40%
    )
    total_score: Mapped[float | None] = mapped_column(
        Numeric(5, 2), nullable=True  # Weighted total out of 100
    )
    letter_grade: Mapped[str | None] = mapped_column(
        String(2), nullable=True  # A+, A, A-, B+, ..., F
    )
    grade_points: Mapped[float | None] = mapped_column(
        Numeric(3, 2), nullable=True  # 4.00, 3.70, 3.30, ...
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    enrollment: Mapped["Enrollment"] = relationship(
        "Enrollment", back_populates="grade"
    )

    def __repr__(self) -> str:
        return f"<Grade(enrollment={self.enrollment_id}, total={self.total_score}, letter={self.letter_grade})>"
