"""
Attendance schemas - request/response models for attendance tracking.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import date, datetime
from app.models.attendance import AttendanceStatus


class AttendanceRecord(BaseModel):
    """Single attendance record entry."""
    enrollment_id: UUID
    status: AttendanceStatus
    notes: Optional[str] = None


class BulkAttendanceEntry(BaseModel):
    """Bulk attendance entry for a class session."""
    teaching_unit_id: UUID
    date: date
    records: List[AttendanceRecord]


class AttendanceResponse(BaseModel):
    """Attendance record response."""
    id: UUID
    enrollment_id: UUID
    student_code: Optional[str] = None
    student_name: Optional[str] = None
    teaching_unit_id: UUID
    date: date
    status: AttendanceStatus
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AttendanceSummary(BaseModel):
    """Attendance summary for a student in a course."""
    enrollment_id: UUID
    course_code: str
    course_name: str
    total_sessions: int
    present_count: int
    absent_count: int
    excused_count: int
    attendance_percentage: float
    is_below_minimum: bool


class ClassAttendanceReport(BaseModel):
    """Attendance report for an entire class."""
    teaching_unit_id: UUID
    course_code: str
    course_name: str
    group_number: int
    date: date
    total_students: int
    present: int
    absent: int
    excused: int
    records: List[AttendanceResponse] = []
