"""
RegistrationCart model - student course selection before enrollment.
"""

import uuid
from datetime import datetime
from sqlalchemy import Integer, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import enum


class CartStatus(str, enum.Enum):
    """Registration cart status workflow."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    ENROLLED = "enrolled"


class RegistrationCart(Base):
    """
    Registration Carts table - holds student course selections.
    Workflow: draft → submitted → approved/rejected → enrolled
    
    A student creates a cart, adds courses, submits for advisor approval,
    then upon approval and payment, courses are enrolled.
    """
    __tablename__ = "registration_carts"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("students.id"), nullable=False
    )
    semester_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("semesters.id"), nullable=False
    )
    status: Mapped[CartStatus] = mapped_column(
        SAEnum(CartStatus), default=CartStatus.DRAFT
    )
    total_hours: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    student: Mapped["Student"] = relationship(
        "Student", back_populates="registration_carts"
    )
    semester: Mapped["Semester"] = relationship(
        "Semester", back_populates="registration_carts"
    )
    items: Mapped[list["RegistrationItem"]] = relationship(
        "RegistrationItem", back_populates="cart", cascade="all, delete-orphan"
    )
    approval: Mapped["AdvisorApproval"] = relationship(
        "AdvisorApproval", back_populates="cart", uselist=False
    )

    def __repr__(self) -> str:
        return f"<RegistrationCart(id={self.id}, status={self.status}, hours={self.total_hours})>"
