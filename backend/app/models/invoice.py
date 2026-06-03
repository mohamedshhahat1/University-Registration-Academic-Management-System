"""
Invoice model - student tuition invoices.
"""

import uuid
from datetime import datetime, date
from sqlalchemy import Numeric, Date, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import enum


class InvoiceStatus(str, enum.Enum):
    """Invoice payment status."""
    DRAFT = "draft"
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    CANCELLED = "cancelled"


class Invoice(Base):
    """
    Invoices table - tuition bills for students per semester.
    Calculates: credit_hours_cost + fixed_fees - scholarship_discount = total_amount
    Tracks payments against total to determine status.
    """
    __tablename__ = "invoices"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("students.id"), nullable=False
    )
    semester_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("semesters.id"), nullable=False
    )
    credit_hours_cost: Mapped[float] = mapped_column(
        Numeric(10, 2), default=0.00, nullable=False
    )
    fixed_fees: Mapped[float] = mapped_column(
        Numeric(10, 2), default=0.00, nullable=False
    )
    scholarship_discount: Mapped[float] = mapped_column(
        Numeric(10, 2), default=0.00, nullable=False
    )
    total_amount: Mapped[float] = mapped_column(
        Numeric(10, 2), default=0.00, nullable=False
    )
    paid_amount: Mapped[float] = mapped_column(
        Numeric(10, 2), default=0.00, nullable=False
    )
    status: Mapped[InvoiceStatus] = mapped_column(
        SAEnum(InvoiceStatus), default=InvoiceStatus.DRAFT
    )
    due_date: Mapped[date | None] = mapped_column(
        Date, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    student: Mapped["Student"] = relationship(
        "Student", back_populates="invoices"
    )
    semester: Mapped["Semester"] = relationship(
        "Semester", back_populates="invoices"
    )
    payments: Mapped[list["Payment"]] = relationship(
        "Payment", back_populates="invoice"
    )

    def __repr__(self) -> str:
        return f"<Invoice(id={self.id}, total={self.total_amount}, status={self.status})>"
