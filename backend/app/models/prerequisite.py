"""
Prerequisite model - course prerequisite relationships.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Prerequisite(Base):
    """
    Prerequisites table - defines course dependency chains.
    A course can have multiple prerequisites, each with a minimum grade.
    Example: Algorithms requires Data Structures with minimum grade C.
    """
    __tablename__ = "prerequisites"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("courses.id"), nullable=False
    )
    prerequisite_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("courses.id"), nullable=False
    )
    min_grade: Mapped[str] = mapped_column(
        String(2), default="D", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    # Relationships
    course: Mapped["Course"] = relationship(
        "Course", back_populates="prerequisites",
        foreign_keys=[course_id]
    )
    prerequisite_course: Mapped["Course"] = relationship(
        "Course", back_populates="required_by",
        foreign_keys=[prerequisite_id]
    )

    def __repr__(self) -> str:
        return f"<Prerequisite(course={self.course_id}, prereq={self.prerequisite_id}, min={self.min_grade})>"
