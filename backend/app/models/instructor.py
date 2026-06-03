"""
Instructor model - extended instructor profile linked to a user.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Instructor(Base):
    """
    Instructors table - stores academic profile for users with instructor role.
    Links to user and department. Teaches through teaching units.
    """
    __tablename__ = "instructors"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), unique=True, nullable=False
    )
    department_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("departments.id"), nullable=False
    )
    specialization: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    academic_rank: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User", back_populates="instructor"
    )
    department: Mapped["Department"] = relationship(
        "Department", back_populates="instructors"
    )
    teaching_units: Mapped[list["TeachingUnit"]] = relationship(
        "TeachingUnit", back_populates="instructor"
    )

    def __repr__(self) -> str:
        return f"<Instructor(id={self.id}, specialization={self.specialization})>"
