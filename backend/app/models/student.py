"""
Student model - extended student profile linked to a user.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Numeric, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import enum


class AcademicStatus(str, enum.Enum):
    """Student academic standing."""
    GOOD_STANDING = "good_standing"
    WARNING = "warning"
    PROBATION = "probation"
    DISMISSED = "dismissed"


class EnrollmentStatus(str, enum.Enum):
    """Student enrollment status."""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    GRADUATED = "graduated"
    WITHDRAWN = "withdrawn"


class Student(Base):
    """
    Students table - stores academic profile for users with student role.
    Links to user, department, program, and advisor.
    Tracks CGPA, total hours, and academic/enrollment status.
    """
    __tablename__ = "students"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), unique=True, nullable=False
    )
    student_code: Mapped[str] = mapped_column(
        String(20), unique=True, index=True, nullable=False
    )
    department_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("departments.id"), nullable=False
    )
    program_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("programs.id"), nullable=False
    )
    advisor_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    admission_year: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    level: Mapped[int] = mapped_column(
        Integer, default=1, nullable=False
    )
    cgpa: Mapped[float] = mapped_column(
        Numeric(3, 2), default=0.00, nullable=False
    )
    total_hours: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    academic_status: Mapped[AcademicStatus] = mapped_column(
        SAEnum(AcademicStatus), default=AcademicStatus.GOOD_STANDING
    )
    enrollment_status: Mapped[EnrollmentStatus] = mapped_column(
        SAEnum(EnrollmentStatus), default=EnrollmentStatus.ACTIVE
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User", back_populates="student", foreign_keys=[user_id]
    )
    department: Mapped["Department"] = relationship(
        "Department", back_populates="students"
    )
    program: Mapped["Program"] = relationship(
        "Program", back_populates="students"
    )
    advisor = relationship("User", foreign_keys=[advisor_id])
    registration_carts: Mapped[list["RegistrationCart"]] = relationship(
        "RegistrationCart", back_populates="student"
    )
    enrollments: Mapped[list["Enrollment"]] = relationship(
        "Enrollment", back_populates="student"
    )
    invoices: Mapped[list["Invoice"]] = relationship(
        "Invoice", back_populates="student"
    )
    semester_gpas: Mapped[list["SemesterGPA"]] = relationship(
        "SemesterGPA", back_populates="student"
    )
    academic_warnings: Mapped[list["AcademicWarning"]] = relationship(
        "AcademicWarning", back_populates="student"
    )

    def __repr__(self) -> str:
        return f"<Student(id={self.id}, code={self.student_code}, cgpa={self.cgpa})>"
