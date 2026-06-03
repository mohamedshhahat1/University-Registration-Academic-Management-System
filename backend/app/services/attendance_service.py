"""
Attendance service - handles attendance tracking and warnings.
"""

from typing import List
from uuid import UUID
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.core.config import settings
from app.models.enrollment import Enrollment, EnrollmentItemStatus
from app.models.teaching_unit import TeachingUnit
from app.models.course_offering import CourseOffering
from app.models.attendance import Attendance, AttendanceStatus
from app.models.academic_warning import AcademicWarning, WarningType
from app.models.student import Student
from app.schemas.attendance import (
    BulkAttendanceEntry,
    AttendanceSummary,
    ClassAttendanceReport,
    AttendanceResponse,
)


class AttendanceService:
    """Service for attendance operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def record_bulk_attendance(
        self, entry: BulkAttendanceEntry
    ) -> List[Attendance]:
        """
        Record attendance for an entire class session.
        Instructor submits all student statuses at once.
        """
        records = []
        for record in entry.records:
            # Check if already recorded for this date
            existing = await self.db.execute(
                select(Attendance).where(
                    and_(
                        Attendance.enrollment_id == record.enrollment_id,
                        Attendance.teaching_unit_id == entry.teaching_unit_id,
                        Attendance.date == entry.date,
                    )
                )
            )
            attendance = existing.scalar_one_or_none()

            if attendance:
                # Update existing record
                attendance.status = record.status
                attendance.notes = record.notes
            else:
                # Create new record
                attendance = Attendance(
                    enrollment_id=record.enrollment_id,
                    teaching_unit_id=entry.teaching_unit_id,
                    date=entry.date,
                    status=record.status,
                    notes=record.notes,
                )
                self.db.add(attendance)

            records.append(attendance)

        await self.db.flush()

        # Check for attendance warnings
        for record in entry.records:
            if record.status == AttendanceStatus.ABSENT:
                await self._check_attendance_warning(record.enrollment_id)

        return records

    async def get_student_attendance_summary(
        self, student_id: UUID, semester_id: UUID
    ) -> List[AttendanceSummary]:
        """Get attendance summary for all courses in a semester."""
        # Get enrollments for the semester
        enrollments_result = await self.db.execute(
            select(Enrollment)
            .where(
                and_(
                    Enrollment.student_id == student_id,
                    Enrollment.semester_id == semester_id,
                    Enrollment.status == EnrollmentItemStatus.ENROLLED,
                )
            )
            .options(
                selectinload(Enrollment.teaching_unit)
                .selectinload(TeachingUnit.offering)
                .selectinload(CourseOffering.course),
            )
        )
        enrollments = enrollments_result.scalars().all()

        summaries = []
        for enrollment in enrollments:
            # Count attendance records
            total_result = await self.db.execute(
                select(func.count(Attendance.id)).where(
                    Attendance.enrollment_id == enrollment.id
                )
            )
            total_sessions = total_result.scalar() or 0

            present_result = await self.db.execute(
                select(func.count(Attendance.id)).where(
                    and_(
                        Attendance.enrollment_id == enrollment.id,
                        Attendance.status == AttendanceStatus.PRESENT,
                    )
                )
            )
            present_count = present_result.scalar() or 0

            absent_result = await self.db.execute(
                select(func.count(Attendance.id)).where(
                    and_(
                        Attendance.enrollment_id == enrollment.id,
                        Attendance.status == AttendanceStatus.ABSENT,
                    )
                )
            )
            absent_count = absent_result.scalar() or 0

            excused_result = await self.db.execute(
                select(func.count(Attendance.id)).where(
                    and_(
                        Attendance.enrollment_id == enrollment.id,
                        Attendance.status == AttendanceStatus.EXCUSED,
                    )
                )
            )
            excused_count = excused_result.scalar() or 0

            # Calculate percentage (excused counts as present)
            effective_present = present_count + excused_count
            percentage = (
                round((effective_present / total_sessions) * 100, 1)
                if total_sessions > 0
                else 100.0
            )

            course = enrollment.teaching_unit.offering.course
            summaries.append(AttendanceSummary(
                enrollment_id=enrollment.id,
                course_code=course.code,
                course_name=course.name,
                total_sessions=total_sessions,
                present_count=present_count,
                absent_count=absent_count,
                excused_count=excused_count,
                attendance_percentage=percentage,
                is_below_minimum=percentage < settings.MIN_ATTENDANCE_PERCENTAGE,
            ))

        return summaries

    async def get_class_attendance(
        self, teaching_unit_id: UUID, attendance_date: date
    ) -> ClassAttendanceReport:
        """Get attendance report for a class on a specific date."""
        # Get teaching unit info
        unit_result = await self.db.execute(
            select(TeachingUnit)
            .where(TeachingUnit.id == teaching_unit_id)
            .options(
                selectinload(TeachingUnit.offering)
                .selectinload(CourseOffering.course)
            )
        )
        unit = unit_result.scalar_one_or_none()
        if not unit:
            raise HTTPException(status_code=404, detail="Teaching unit not found")

        # Get attendance records for that date
        records_result = await self.db.execute(
            select(Attendance)
            .where(
                and_(
                    Attendance.teaching_unit_id == teaching_unit_id,
                    Attendance.date == attendance_date,
                )
            )
            .options(
                selectinload(Attendance.enrollment)
                .selectinload(Enrollment.student)
                .selectinload(Student.user)
            )
        )
        records = records_result.scalars().all()

        present = sum(1 for r in records if r.status == AttendanceStatus.PRESENT)
        absent = sum(1 for r in records if r.status == AttendanceStatus.ABSENT)
        excused = sum(1 for r in records if r.status == AttendanceStatus.EXCUSED)

        return ClassAttendanceReport(
            teaching_unit_id=teaching_unit_id,
            course_code=unit.offering.course.code,
            course_name=unit.offering.course.name,
            group_number=unit.group_number,
            date=attendance_date,
            total_students=len(records),
            present=present,
            absent=absent,
            excused=excused,
            records=[
                AttendanceResponse(
                    id=r.id,
                    enrollment_id=r.enrollment_id,
                    student_code=r.enrollment.student.student_code if r.enrollment.student else None,
                    student_name=r.enrollment.student.user.full_name if r.enrollment.student else None,
                    teaching_unit_id=r.teaching_unit_id,
                    date=r.date,
                    status=r.status,
                    notes=r.notes,
                    created_at=r.created_at,
                )
                for r in records
            ],
        )

    async def _check_attendance_warning(self, enrollment_id: UUID) -> None:
        """Check if attendance has dropped below minimum and issue warning."""
        # Count totals
        total_result = await self.db.execute(
            select(func.count(Attendance.id)).where(
                Attendance.enrollment_id == enrollment_id
            )
        )
        total = total_result.scalar() or 0

        if total < 3:  # Don't warn until at least 3 sessions
            return

        present_result = await self.db.execute(
            select(func.count(Attendance.id)).where(
                and_(
                    Attendance.enrollment_id == enrollment_id,
                    Attendance.status.in_([
                        AttendanceStatus.PRESENT,
                        AttendanceStatus.EXCUSED,
                    ]),
                )
            )
        )
        present = present_result.scalar() or 0

        percentage = (present / total) * 100 if total > 0 else 100

        if percentage < settings.MIN_ATTENDANCE_PERCENTAGE:
            # Get student info from enrollment
            enrollment_result = await self.db.execute(
                select(Enrollment)
                .where(Enrollment.id == enrollment_id)
                .options(selectinload(Enrollment.student))
            )
            enrollment = enrollment_result.scalar_one()

            # Check if warning already exists for this enrollment
            existing_warning = await self.db.execute(
                select(AcademicWarning).where(
                    and_(
                        AcademicWarning.student_id == enrollment.student_id,
                        AcademicWarning.semester_id == enrollment.semester_id,
                        AcademicWarning.type == WarningType.ATTENDANCE_WARNING,
                    )
                )
            )
            if not existing_warning.scalar_one_or_none():
                warning = AcademicWarning(
                    student_id=enrollment.student_id,
                    semester_id=enrollment.semester_id,
                    type=WarningType.ATTENDANCE_WARNING,
                    reason=f"Attendance ({percentage:.1f}%) below minimum ({settings.MIN_ATTENDANCE_PERCENTAGE}%)",
                    warning_number=1,
                )
                self.db.add(warning)
                await self.db.flush()
