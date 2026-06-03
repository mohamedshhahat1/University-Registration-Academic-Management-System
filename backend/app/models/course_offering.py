"""
CourseOffering model - courses offered in a specific semester.
"""

import uuid
from datetime import datetime
from sqlalchemy import Integer, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import enum


class OfferingStatus(str, enum.Enum):
    """Status of a course offering."""
    OPEN = "open"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class CourseOffering(Base):
    """
    Course Offerings table - a specific course available in a semester.
    Tracks capacity and enrollment count.
    Contains teaching units (lecture, section, lab groups).
    """
    __tablename__ = "course_offerings"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("courses.id"), nullable=False
    )
    semester_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("semesters.id"), nullable=False
    )
    max_capacity: Mapped[int] = mapped_column(
        Integer, default=200, nullable=False
    )
    current_enrolled: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    status: Mapped[OfferingStatus] = mapped_column(
        SAEnum(OfferingStatus), default=OfferingStatus.OPEN
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    # Relationships
    course: Mapped["Course"] = relationship(
        "Course", back_populates="offerings"
    )
    semester: Mapped["Semester"] = relationship(
        "Semester", back_populates="course_offerings"
    )
    teaching_units: Mapped[list["TeachingUnit"]] = relationship(
        "TeachingUnit", back_populates="offering"
    )

    def __repr__(self) -> str:
        return f"<CourseOffering(id={self.id}, status={self.status}, enrolled={self.current_enrolled}/{self.max_capacity})>"
