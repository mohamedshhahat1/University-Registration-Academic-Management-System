"""
Attendance API endpoints.
Handles attendance recording and reporting.
"""

from typing import List
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.auth.dependencies import get_current_user, require_instructor
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.semester import Semester
from app.services.attendance_service import AttendanceService
from app.schemas.attendance import (
    BulkAttendanceEntry,
    AttendanceSummary,
    ClassAttendanceReport,
    AttendanceResponse,
)

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.post("/record", response_model=List[AttendanceResponse])
async def record_attendance(
    entry: BulkAttendanceEntry,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    """Record attendance for a class session. Requires instructor or admin role."""
    service = AttendanceService(db)
    records = await service.record_bulk_attendance(entry)
    return [
        AttendanceResponse(
            id=r.id,
            enrollment_id=r.enrollment_id,
            teaching_unit_id=r.teaching_unit_id,
            date=r.date,
            status=r.status,
            notes=r.notes,
            created_at=r.created_at,
        )
        for r in records
    ]


@router.get("/my/summary", response_model=List[AttendanceSummary])
async def get_my_attendance(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get attendance summary for the current student."""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Not a student account")

    student_result = await db.execute(
        select(Student).where(Student.user_id == current_user.id)
    )
    student = student_result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    # Get current semester
    sem_result = await db.execute(
        select(Semester).where(Semester.is_current == True)
    )
    semester = sem_result.scalar_one_or_none()
    if not semester:
        raise HTTPException(status_code=404, detail="No current semester")

    service = AttendanceService(db)
    return await service.get_student_attendance_summary(student.id, semester.id)


@router.get("/class/{teaching_unit_id}", response_model=ClassAttendanceReport)
async def get_class_attendance(
    teaching_unit_id: UUID,
    attendance_date: date,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    """Get attendance report for a class on a specific date."""
    service = AttendanceService(db)
    return await service.get_class_attendance(teaching_unit_id, attendance_date)


@router.get("/student/{student_id}/summary", response_model=List[AttendanceSummary])
async def get_student_attendance(
    student_id: UUID,
    semester_id: UUID = None,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    """Get attendance summary for a specific student. Requires instructor or admin."""
    if not semester_id:
        sem_result = await db.execute(
            select(Semester).where(Semester.is_current == True)
        )
        semester = sem_result.scalar_one_or_none()
        if not semester:
            raise HTTPException(status_code=404, detail="No current semester")
        semester_id = semester.id

    service = AttendanceService(db)
    return await service.get_student_attendance_summary(student_id, semester_id)
