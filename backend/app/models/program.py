"""
Program model - academic programs within departments.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Program(Base):
    """
    Programs table - academic programs like BSc Computer Engineering.
    Each program belongs to a department and has a total credit hours requirement.
    """
    __tablename__ = "programs"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    code: Mapped[str] = mapped_column(
        String(10), unique=True, nullable=False
    )
    department_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("departments.id"), nullable=False
    )
    total_hours: Mapped[int] = mapped_column(
        Integer, nullable=False, default=160
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    # Relationships
    department: Mapped["Department"] = relationship(
        "Department", back_populates="programs"
    )
    students: Mapped[list["Student"]] = relationship(
        "Student", back_populates="program"
    )

    def __repr__(self) -> str:
        return f"<Program(id={self.id}, code={self.code}, name={self.name})>"
