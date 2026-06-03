"""
Payment model - records of payments against invoices.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, Numeric, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import enum


class PaymentMethod(str, enum.Enum):
    """Supported payment methods."""
    CASH = "cash"
    VISA = "visa"
    FAWRY = "fawry"
    INSTAPAY = "instapay"


class PaymentStatus(str, enum.Enum):
    """Payment transaction status."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class Payment(Base):
    """
    Payments table - individual payment transactions against invoices.
    Supports multiple partial payments per invoice.
    """
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    invoice_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("invoices.id"), nullable=False
    )
    amount: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    payment_method: Mapped[PaymentMethod] = mapped_column(
        SAEnum(PaymentMethod), nullable=False
    )
    transaction_ref: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    status: Mapped[PaymentStatus] = mapped_column(
        SAEnum(PaymentStatus), default=PaymentStatus.PENDING
    )
    paid_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    # Relationships
    invoice: Mapped["Invoice"] = relationship(
        "Invoice", back_populates="payments"
    )

    def __repr__(self) -> str:
        return f"<Payment(id={self.id}, amount={self.amount}, method={self.payment_method})>"
