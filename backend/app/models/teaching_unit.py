"""
TeachingUnit model - individual lecture/section/lab groups within an offering.
"""

import uuid
from datetime import datetime
from sqlalchemy import Integer, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import enum


class TeachingUnitType(str, enum.Enum):
    """Types of teaching units."""
    LECTURE = "lecture"
    SECTION = "section"
    LAB = "lab"


class TeachingUnit(Base):
    """
    Teaching Units table - individual class groups within a course offering.
    A course offering may have:
    - 1 lecture group (all students attend)
    - Multiple section groups (students pick one)
    - Multiple lab groups (students pick one)
    Each unit has its own instructor, capacity, and schedule.
    """
    __tablename__ = "teaching_units"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    offering_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("course_offerings.id"), nullable=False
    )
    type: Mapped[TeachingUnitType] = mapped_column(
        SAEnum(TeachingUnitType), nullable=False
    )
    group_number: Mapped[int] = mapped_column(
        Integer, default=1, nullable=False
    )
    instructor_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("instructors.id"), nullable=True
    )
    max_capacity: Mapped[int] = mapped_column(
        Integer, default=40, nullable=False
    )
    current_enrolled: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    # Relationships
    offering: Mapped["CourseOffering"] = relationship(
        "CourseOffering", back_populates="teaching_units"
    )
    instructor: Mapped["Instructor"] = relationship(
        "Instructor", back_populates="teaching_units"
    )
    schedules: Mapped[list["Schedule"]] = relationship(
        "Schedule", back_populates="teaching_unit"
    )
    registration_items: Mapped[list["RegistrationItem"]] = relationship(
        "RegistrationItem", back_populates="teaching_unit"
    )
    enrollments: Mapped[list["Enrollment"]] = relationship(
        "Enrollment", back_populates="teaching_unit"
    )

    def __repr__(self) -> str:
        return f"<TeachingUnit(id={self.id}, type={self.type}, group={self.group_number})>"
