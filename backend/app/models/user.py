"""
User model - core authentication and role management.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import enum


class UserRole(str, enum.Enum):
    """User roles in the system."""
    STUDENT = "student"
    ADVISOR = "advisor"
    INSTRUCTOR = "instructor"
    REGISTRAR = "registrar"
    FINANCE = "finance"
    ADMIN = "admin"


class User(Base):
    """
    Users table - stores all system users regardless of role.
    Role-specific data is stored in related tables (students, instructors).
    """
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    full_name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    phone: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )
    national_id: Mapped[str | None] = mapped_column(
        String(20), unique=True, nullable=True
    )
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    student: Mapped["Student"] = relationship(
        "Student", back_populates="user", uselist=False
    )
    instructor: Mapped["Instructor"] = relationship(
        "Instructor", back_populates="user", uselist=False
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
