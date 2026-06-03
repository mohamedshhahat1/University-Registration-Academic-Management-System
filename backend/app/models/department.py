"""
Department model - academic departments.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Department(Base):
    """
    Departments table - e.g., Communications Engineering, Computer Engineering.
    Each department has a head (instructor/user) and contains programs and courses.
    """
    __tablename__ = "departments"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False
    )
    code: Mapped[str] = mapped_column(
        String(10), unique=True, nullable=False
    )
    head_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    # Relationships
    head = relationship("User", foreign_keys=[head_id])
    programs: Mapped[list["Program"]] = relationship(
        "Program", back_populates="department"
    )
    courses: Mapped[list["Course"]] = relationship(
        "Course", back_populates="department"
    )
    students: Mapped[list["Student"]] = relationship(
        "Student", back_populates="department"
    )
    instructors: Mapped[list["Instructor"]] = relationship(
        "Instructor", back_populates="department"
    )

    def __repr__(self) -> str:
        return f"<Department(id={self.id}, code={self.code}, name={self.name})>"
