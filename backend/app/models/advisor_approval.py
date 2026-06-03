"""
AdvisorApproval model - advisor review of registration carts.
"""

import uuid
from datetime import datetime
from sqlalchemy import Text, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import enum


class ApprovalStatus(str, enum.Enum):
    """Advisor approval status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class AdvisorApproval(Base):
    """
    Advisor Approvals table - tracks advisor review of registration carts.
    Advisor can approve, reject with comments, or leave pending.
    """
    __tablename__ = "advisor_approvals"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    cart_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("registration_carts.id"), unique=True, nullable=False
    )
    advisor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    status: Mapped[ApprovalStatus] = mapped_column(
        SAEnum(ApprovalStatus), default=ApprovalStatus.PENDING
    )
    comments: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    # Relationships
    cart: Mapped["RegistrationCart"] = relationship(
        "RegistrationCart", back_populates="approval"
    )
    advisor = relationship("User", foreign_keys=[advisor_id])

    def __repr__(self) -> str:
        return f"<AdvisorApproval(cart={self.cart_id}, status={self.status})>"
