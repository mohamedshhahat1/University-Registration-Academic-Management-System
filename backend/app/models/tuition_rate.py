"""
TuitionRate model - cost per credit hour by academic year (cohort-based).
"""

import uuid
from datetime import datetime
from sqlalchemy import String, Numeric, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class TuitionRate(Base):
    """
    Tuition Rates table - defines cost structure per academic year.
    Supports cohort-based pricing: students keep their admission year rate.
    """
    __tablename__ = "tuition_rates"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    academic_year: Mapped[str] = mapped_column(
        String(9), unique=True, nullable=False  # e.g., "2024/2025"
    )
    cost_per_hour: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    fixed_fees: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<TuitionRate(year={self.academic_year}, per_hour={self.cost_per_hour})>"
