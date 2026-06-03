"""
Course model - academic courses offered by departments.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Course(Base):
    """
    Courses table - defines academic courses.
    Each course belongs to a department and may have prerequisites.
    Courses can have different teaching components (lecture, section, lab).
    """
    __tablename__ = "courses"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    code: Mapped[str] = mapped_column(
        String(10), unique=True, index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    credit_hours: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    department_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("departments.id"), nullable=False
    )
    has_lecture: Mapped[bool] = mapped_column(
        Boolean, default=True
    )
    has_section: Mapped[bool] = mapped_column(
        Boolean, default=False
    )
    has_lab: Mapped[bool] = mapped_column(
        Boolean, default=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    # Relationships
    department: Mapped["Department"] = relationship(
        "Department", back_populates="courses"
    )
    prerequisites: Mapped[list["Prerequisite"]] = relationship(
        "Prerequisite",
        back_populates="course",
        foreign_keys="Prerequisite.course_id"
    )
    required_by: Mapped[list["Prerequisite"]] = relationship(
        "Prerequisite",
        back_populates="prerequisite_course",
        foreign_keys="Prerequisite.prerequisite_id"
    )
    offerings: Mapped[list["CourseOffering"]] = relationship(
        "CourseOffering", back_populates="course"
    )

    def __repr__(self) -> str:
        return f"<Course(id={self.id}, code={self.code}, name={self.name})>"
