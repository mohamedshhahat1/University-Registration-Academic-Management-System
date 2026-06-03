"""
Registration schemas - request/response models for course registration.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime, time
from app.models.registration_cart import CartStatus
from app.models.advisor_approval import ApprovalStatus
from app.models.teaching_unit import TeachingUnitType
from app.models.schedule import DayOfWeek


class CourseOfferingResponse(BaseModel):
    """Course offering with availability info."""
    id: UUID
    course_id: UUID
    course_code: str
    course_name: str
    credit_hours: int
    semester_id: UUID
    teaching_unit_id: Optional[UUID] = None
    max_capacity: int
    current_enrolled: int
    available_seats: int
    status: str

    class Config:
        from_attributes = True


class TeachingUnitResponse(BaseModel):
    """Teaching unit details."""
    id: UUID
    offering_id: UUID
    type: TeachingUnitType
    group_number: int
    instructor_name: Optional[str] = None
    max_capacity: int
    current_enrolled: int
    available_seats: int

    class Config:
        from_attributes = True


class ScheduleResponse(BaseModel):
    """Schedule time slot."""
    id: UUID
    day_of_week: DayOfWeek
    start_time: time
    end_time: time
    classroom_name: Optional[str] = None
    building: Optional[str] = None

    class Config:
        from_attributes = True


class TeachingUnitWithSchedule(BaseModel):
    """Teaching unit with its schedule."""
    unit: TeachingUnitResponse
    schedules: List[ScheduleResponse] = []


class AddToCartRequest(BaseModel):
    """Add a teaching unit to registration cart."""
    teaching_unit_id: UUID


class RemoveFromCartRequest(BaseModel):
    """Remove a teaching unit from registration cart."""
    teaching_unit_id: UUID


class RegistrationItemResponse(BaseModel):
    """Registration item details."""
    id: UUID
    teaching_unit_id: UUID
    course_code: str
    course_name: str
    credit_hours: int
    unit_type: TeachingUnitType
    group_number: int
    schedules: List[ScheduleResponse] = []

    class Config:
        from_attributes = True


class RegistrationCartResponse(BaseModel):
    """Full registration cart."""
    id: UUID
    student_id: UUID
    semester_id: UUID
    status: CartStatus
    total_hours: int
    items: List[RegistrationItemResponse] = []
    submitted_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SubmitCartRequest(BaseModel):
    """Submit cart for advisor approval."""
    pass  # No additional data needed


class ApprovalResponse(BaseModel):
    """Advisor approval status."""
    id: UUID
    cart_id: UUID
    advisor_id: UUID
    advisor_name: Optional[str] = None
    status: ApprovalStatus
    comments: Optional[str] = None
    reviewed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ApprovalDecisionRequest(BaseModel):
    """Advisor approval/rejection decision."""
    status: ApprovalStatus
    comments: Optional[str] = None


class ValidationError(BaseModel):
    """Registration validation error."""
    error_type: str  # prerequisite, conflict, capacity, credit_limit
    message: str
    course_code: Optional[str] = None
    details: Optional[dict] = None


class RegistrationValidationResponse(BaseModel):
    """Result of registration validation."""
    is_valid: bool
    errors: List[ValidationError] = []
    total_hours: int
    max_allowed_hours: int
