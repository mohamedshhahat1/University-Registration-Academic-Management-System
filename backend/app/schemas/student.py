"""
Student schemas - request/response models for student endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.models.student import AcademicStatus, EnrollmentStatus


class StudentCreate(BaseModel):
    """Create a new student profile."""
    user_id: UUID
    student_code: str = Field(..., max_length=20)
    department_id: UUID
    program_id: UUID
    advisor_id: Optional[UUID] = None
    admission_year: int = Field(..., ge=2000, le=2100)
    level: int = Field(default=1, ge=1, le=6)


class StudentUpdate(BaseModel):
    """Update student profile."""
    department_id: Optional[UUID] = None
    program_id: Optional[UUID] = None
    advisor_id: Optional[UUID] = None
    level: Optional[int] = Field(None, ge=1, le=6)
    academic_status: Optional[AcademicStatus] = None
    enrollment_status: Optional[EnrollmentStatus] = None


class StudentResponse(BaseModel):
    """Student profile response."""
    id: UUID
    user_id: UUID
    student_code: str
    department_id: UUID
    program_id: UUID
    advisor_id: Optional[UUID] = None
    admission_year: int
    level: int
    cgpa: float
    total_hours: int
    academic_status: AcademicStatus
    enrollment_status: EnrollmentStatus
    created_at: datetime

    class Config:
        from_attributes = True


class StudentDashboard(BaseModel):
    """Student dashboard summary."""
    student_code: str
    full_name: str
    department: str
    program: str
    level: int
    cgpa: float
    total_hours: int
    current_semester_hours: int
    academic_status: AcademicStatus
    enrollment_status: EnrollmentStatus
    tuition_balance: float
    warnings_count: int
