"""
Semester model - academic terms with registration periods.
"""

import uuid
from datetime import datetime, date
from sqlalchemy import String, Boolean, Date, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import enum


class SemesterType(str, enum.Enum):
    """Types of academic semesters."""
    FALL = "fall"
    SPRING = "spring"
    SUMMER = "summer"


class Semester(Base):
    """
    Semesters table - defines academic terms.
    Includes registration period dates, add/drop, and withdrawal deadlines.
    Only one semester can be current at a time.
    """
    __tablename__ = "semesters"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(
        String(50), nullable=False
    )
    type: Mapped[SemesterType] = mapped_column(
        SAEnum(SemesterType), nullable=False
    )
    academic_year: Mapped[str] = mapped_column(
        String(9), nullable=False  # e.g., "2024/2025"
    )
    start_date: Mapped[date] = mapped_column(
        Date, nullable=False
    )
    end_date: Mapped[date] = mapped_column(
        Date, nullable=False
    )
    registration_start: Mapped[date] = mapped_column(
        Date, nullable=False
    )
    registration_end: Mapped[date] = mapped_column(
        Date, nullable=False
    )
    add_drop_end: Mapped[date] = mapped_column(
        Date, nullable=False
    )
    withdrawal_end: Mapped[date] = mapped_column(
        Date, nullable=False
    )
    is_current: Mapped[bool] = mapped_column(
        Boolean, default=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    # Relationships
    course_offerings: Mapped[list["CourseOffering"]] = relationship(
        "CourseOffering", back_populates="semester"
    )
    registration_carts: Mapped[list["RegistrationCart"]] = relationship(
        "RegistrationCart", back_populates="semester"
    )
    enrollments: Mapped[list["Enrollment"]] = relationship(
        "Enrollment", back_populates="semester"
    )
    invoices: Mapped[list["Invoice"]] = relationship(
        "Invoice", back_populates="semester"
    )
    semester_gpas: Mapped[list["SemesterGPA"]] = relationship(
        "SemesterGPA", back_populates="semester"
    )

    def __repr__(self) -> str:
        return f"<Semester(id={self.id}, name={self.name}, current={self.is_current})>"
