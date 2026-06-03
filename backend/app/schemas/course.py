"""
Course schemas - request/response models for course management.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class CourseCreate(BaseModel):
    """Create a new course."""
    code: str = Field(..., max_length=10)
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    credit_hours: int = Field(..., ge=1, le=6)
    department_id: UUID
    has_lecture: bool = True
    has_section: bool = False
    has_lab: bool = False


class CourseUpdate(BaseModel):
    """Update course details."""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    credit_hours: Optional[int] = Field(None, ge=1, le=6)
    has_lecture: Optional[bool] = None
    has_section: Optional[bool] = None
    has_lab: Optional[bool] = None
    is_active: Optional[bool] = None


class CourseResponse(BaseModel):
    """Course information response."""
    id: UUID
    code: str
    name: str
    description: Optional[str] = None
    credit_hours: int
    department_id: UUID
    has_lecture: bool
    has_section: bool
    has_lab: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PrerequisiteCreate(BaseModel):
    """Add a prerequisite to a course."""
    prerequisite_id: UUID
    min_grade: str = Field(default="D", max_length=2)


class PrerequisiteResponse(BaseModel):
    """Prerequisite relationship response."""
    id: UUID
    course_id: UUID
    prerequisite_id: UUID
    prerequisite_code: Optional[str] = None
    prerequisite_name: Optional[str] = None
    min_grade: str

    class Config:
        from_attributes = True


class CourseWithPrerequisites(BaseModel):
    """Course with its prerequisites list."""
    course: CourseResponse
    prerequisites: List[PrerequisiteResponse] = []
