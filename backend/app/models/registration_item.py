"""
RegistrationItem model - individual course selections in a cart.
"""

import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class RegistrationItem(Base):
    """
    Registration Items table - individual teaching unit selections.
    Each item in a cart represents one teaching unit the student wants to register for.
    """
    __tablename__ = "registration_items"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    cart_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("registration_carts.id"), nullable=False
    )
    teaching_unit_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("teaching_units.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    # Relationships
    cart: Mapped["RegistrationCart"] = relationship(
        "RegistrationCart", back_populates="items"
    )
    teaching_unit: Mapped["TeachingUnit"] = relationship(
        "TeachingUnit", back_populates="registration_items"
    )

    def __repr__(self) -> str:
        return f"<RegistrationItem(cart={self.cart_id}, unit={self.teaching_unit_id})>"
