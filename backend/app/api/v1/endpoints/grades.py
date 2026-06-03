"""
Grades API endpoints.
Handles grade entry, GPA calculation, and transcripts.
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.auth.dependencies import get_current_user, require_instructor
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.enrollment import Enrollment, EnrollmentItemStatus
from app.models.teaching_unit import TeachingUnit
from app.models.course_offering import CourseOffering
from app.models.grade import Grade
from app.services.grade_service import GradeService
from app.schemas.grade import (
    GradeEntry,
    GradeResponse,
    BulkGradeEntry,
    GPACalculationResult,
    TranscriptResponse,
)

router = APIRouter(prefix="/grades", tags=["Grades"])


@router.post("/enter", response_model=GradeResponse)
async def enter_grade(
    grade_entry: GradeEntry,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    """Enter or update grade for a student. Requires instructor or admin role."""
    service = GradeService(db)
    grade = await service.enter_grade(grade_entry)
    return GradeResponse(
        id=grade.id,
        enrollment_id=grade.enrollment_id,
        midterm1=float(grade.midterm1) if grade.midterm1 else None,
        midterm2=float(grade.midterm2) if grade.midterm2 else None,
        coursework=float(grade.coursework) if grade.coursework else None,
        final_exam=float(grade.final_exam) if grade.final_exam else None,
        total_score=float(grade.total_score) if grade.total_score else None,
        letter_grade=grade.letter_grade,
        grade_points=float(grade.grade_points) if grade.grade_points else None,
        created_at=grade.created_at,
    )


@router.post("/enter/bulk", response_model=List[GradeResponse])
async def enter_bulk_grades(
    bulk_entry: BulkGradeEntry,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    """Enter grades for multiple students at once."""
    service = GradeService(db)
    grades = await service.enter_bulk_grades(bulk_entry.grades)
    return [
        GradeResponse(
            id=g.id,
            enrollment_id=g.enrollment_id,
            midterm1=float(g.midterm1) if g.midterm1 else None,
            midterm2=float(g.midterm2) if g.midterm2 else None,
            coursework=float(g.coursework) if g.coursework else None,
            final_exam=float(g.final_exam) if g.final_exam else None,
            total_score=float(g.total_score) if g.total_score else None,
            letter_grade=g.letter_grade,
            grade_points=float(g.grade_points) if g.grade_points else None,
            created_at=g.created_at,
        )
        for g in grades
    ]


@router.get("/my", response_model=List[GradeResponse])
async def get_my_grades(
    semester_id: UUID = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get grades for the current student."""
    student_result = await db.execute(
        select(Student).where(Student.user_id == current_user.id)
    )
    student = student_result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    query = (
        select(Grade)
        .join(Enrollment)
        .where(Enrollment.student_id == student.id)
    )
    if semester_id:
        query = query.where(Enrollment.semester_id == semester_id)

    result = await db.execute(
        query.options(
            selectinload(Grade.enrollment)
            .selectinload(Enrollment.teaching_unit)
            .selectinload(TeachingUnit.offering)
            .selectinload(CourseOffering.course)
        )
    )
    grades = result.scalars().all()

    return [
        GradeResponse(
            id=g.id,
            enrollment_id=g.enrollment_id,
            course_code=g.enrollment.teaching_unit.offering.course.code,
            course_name=g.enrollment.teaching_unit.offering.course.name,
            credit_hours=g.enrollment.teaching_unit.offering.course.credit_hours,
            midterm1=float(g.midterm1) if g.midterm1 else None,
            midterm2=float(g.midterm2) if g.midterm2 else None,
            coursework=float(g.coursework) if g.coursework else None,
            final_exam=float(g.final_exam) if g.final_exam else None,
            total_score=float(g.total_score) if g.total_score else None,
            letter_grade=g.letter_grade,
            grade_points=float(g.grade_points) if g.grade_points else None,
            created_at=g.created_at,
        )
        for g in grades
    ]


@router.post("/calculate-gpa/{student_id}/{semester_id}", response_model=GPACalculationResult)
async def calculate_gpa(
    student_id: UUID,
    semester_id: UUID,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    """Calculate semester GPA and update CGPA for a student."""
    service = GradeService(db)
    return await service.calculate_semester_gpa(student_id, semester_id)


@router.get("/transcript/{student_id}", response_model=TranscriptResponse)
async def get_transcript(
    student_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get full academic transcript for a student."""
    # Students can only view their own transcript
    if current_user.role == UserRole.STUDENT:
        student_result = await db.execute(
            select(Student).where(Student.user_id == current_user.id)
        )
        student = student_result.scalar_one_or_none()
        if not student or student.id != student_id:
            raise HTTPException(status_code=403, detail="Can only view your own transcript")

    service = GradeService(db)
    return await service.get_transcript(student_id)


@router.get("/teaching-unit/{unit_id}/students", response_model=List[GradeResponse])
async def get_unit_grades(
    unit_id: UUID,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    """Get all grades for students in a teaching unit. For instructor grade management."""
    result = await db.execute(
        select(Enrollment)
        .where(
            and_(
                Enrollment.teaching_unit_id == unit_id,
                Enrollment.status == EnrollmentItemStatus.ENROLLED,
            )
        )
        .options(
            selectinload(Enrollment.grade),
            selectinload(Enrollment.student).selectinload(Student.user),
        )
    )
    enrollments = result.scalars().all()

    grades = []
    for enrollment in enrollments:
        grade = enrollment.grade
        grades.append(GradeResponse(
            id=grade.id if grade else None,
            enrollment_id=enrollment.id,
            student_code=enrollment.student.student_code,
            student_name=enrollment.student.user.full_name,
            midterm1=float(grade.midterm1) if grade and grade.midterm1 else None,
            midterm2=float(grade.midterm2) if grade and grade.midterm2 else None,
            coursework=float(grade.coursework) if grade and grade.coursework else None,
            final_exam=float(grade.final_exam) if grade and grade.final_exam else None,
            total_score=float(grade.total_score) if grade and grade.total_score else None,
            letter_grade=grade.letter_grade if grade else None,
            grade_points=float(grade.grade_points) if grade and grade.grade_points else None,
            created_at=grade.created_at if grade else enrollment.created_at,
        ))

    return grades
