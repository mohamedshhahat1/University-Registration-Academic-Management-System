"""
Classroom model - physical rooms for scheduling.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import enum


class ClassroomType(str, enum.Enum):
    """Types of classrooms."""
    LECTURE_HALL = "lecture_hall"
    LAB = "lab"
    TUTORIAL_ROOM = "tutorial_room"


class Classroom(Base):
    """
    Classrooms table - physical rooms available for scheduling.
    Each room has a type, capacity, and building location.
    """
    __tablename__ = "classrooms"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )
    building: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    capacity: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    type: Mapped[ClassroomType] = mapped_column(
        SAEnum(ClassroomType), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    # Relationships
    schedules: Mapped[list["Schedule"]] = relationship(
        "Schedule", back_populates="classroom"
    )

    def __repr__(self) -> str:
        return f"<Classroom(id={self.id}, name={self.name}, building={self.building})>"
