"""
Semester schemas - request/response models for semester management.
"""

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import date, datetime
from app.models.semester import SemesterType


class SemesterCreate(BaseModel):
    """Create a new semester."""
    name: str = Field(..., max_length=50)
    type: SemesterType
    academic_year: str = Field(..., pattern=r"^\d{4}/\d{4}$")
    start_date: date
    end_date: date
    registration_start: date
    registration_end: date
    add_drop_end: date
    withdrawal_end: date


class SemesterUpdate(BaseModel):
    """Update semester details."""
    name: Optional[str] = Field(None, max_length=50)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    registration_start: Optional[date] = None
    registration_end: Optional[date] = None
    add_drop_end: Optional[date] = None
    withdrawal_end: Optional[date] = None
    is_current: Optional[bool] = None


class SemesterResponse(BaseModel):
    """Semester information response."""
    id: UUID
    name: str
    type: SemesterType
    academic_year: str
    start_date: date
    end_date: date
    registration_start: date
    registration_end: date
    add_drop_end: date
    withdrawal_end: date
    is_current: bool
    created_at: datetime

    class Config:
        from_attributes = True
