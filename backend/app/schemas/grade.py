"""
Grade schemas - request/response models for grading and GPA.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class GradeEntry(BaseModel):
    """Enter/update grade components for a student."""
    enrollment_id: UUID
    midterm1: Optional[float] = Field(None, ge=0, le=100)
    midterm2: Optional[float] = Field(None, ge=0, le=100)
    coursework: Optional[float] = Field(None, ge=0, le=100)
    final_exam: Optional[float] = Field(None, ge=0, le=100)


class GradeResponse(BaseModel):
    """Grade details response."""
    id: UUID
    enrollment_id: UUID
    student_code: Optional[str] = None
    student_name: Optional[str] = None
    course_code: Optional[str] = None
    course_name: Optional[str] = None
    credit_hours: Optional[int] = None
    midterm1: Optional[float] = None
    midterm2: Optional[float] = None
    coursework: Optional[float] = None
    final_exam: Optional[float] = None
    total_score: Optional[float] = None
    letter_grade: Optional[str] = None
    grade_points: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class BulkGradeEntry(BaseModel):
    """Bulk grade entry for an instructor's class."""
    grades: List[GradeEntry]


class SemesterGPAResponse(BaseModel):
    """Semester GPA record."""
    semester_name: str
    academic_year: str
    gpa: float
    total_hours: int
    total_points: float

    class Config:
        from_attributes = True


class TranscriptEntry(BaseModel):
    """Single course entry in transcript."""
    course_code: str
    course_name: str
    credit_hours: int
    letter_grade: str
    grade_points: float
    semester_name: str


class TranscriptResponse(BaseModel):
    """Full student transcript."""
    student_code: str
    student_name: str
    department: str
    program: str
    entries: List[TranscriptEntry] = []
    semester_gpas: List[SemesterGPAResponse] = []
    cgpa: float
    total_hours: int
    total_points: float


class GPACalculationResult(BaseModel):
    """Result of GPA/CGPA calculation."""
    semester_gpa: float
    cumulative_gpa: float
    semester_hours: int
    total_hours: int
    semester_points: float
    total_points: float


class GradeScale(BaseModel):
    """Grade scale entry."""
    letter: str
    min_score: float
    max_score: float
    points: float
