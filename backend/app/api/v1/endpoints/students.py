"""
Student API endpoints.
Handles student profile management and dashboard.
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.auth.dependencies import get_current_user, require_admin, require_registrar
from app.models.user import User, UserRole
from app.models.student import Student
from app.schemas.student import (
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    StudentDashboard,
)

router = APIRouter(prefix="/students", tags=["Students"])


@router.post("/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
async def create_student(
    student_data: StudentCreate,
    current_user: User = Depends(require_registrar),
    db: AsyncSession = Depends(get_db),
):
    """Create a new student profile. Requires registrar or admin role."""
    student = Student(**student_data.model_dump())
    db.add(student)
    await db.flush()
    return StudentResponse.model_validate(student)


@router.get("/", response_model=List[StudentResponse])
async def list_students(
    department_id: UUID = None,
    program_id: UUID = None,
    current_user: User = Depends(require_registrar),
    db: AsyncSession = Depends(get_db),
):
    """List all students. Supports filtering by department and program."""
    query = select(Student)
    if department_id:
        query = query.where(Student.department_id == department_id)
    if program_id:
        query = query.where(Student.program_id == program_id)
    
    result = await db.execute(query.order_by(Student.student_code))
    return [StudentResponse.model_validate(s) for s in result.scalars().all()]


@router.get("/me/dashboard", response_model=StudentDashboard)
async def get_my_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get dashboard data for the current student."""
    if current_user.role != UserRole.STUDENT:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Not a student account")

    result = await db.execute(
        select(Student)
        .where(Student.user_id == current_user.id)
        .options(
            selectinload(Student.user),
            selectinload(Student.department),
            selectinload(Student.program),
            selectinload(Student.academic_warnings),
        )
    )
    student = result.scalar_one_or_none()
    if not student:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Student profile not found")

    # Calculate current semester hours (from active enrollments)
    from app.models.enrollment import Enrollment, EnrollmentItemStatus
    from app.models.teaching_unit import TeachingUnit
    from app.models.course_offering import CourseOffering
    from app.models.semester import Semester
    from sqlalchemy import and_, func

    current_semester = await db.execute(
        select(Semester).where(Semester.is_current == True)
    )
    semester = current_semester.scalar_one_or_none()
    current_hours = 0
    tuition_balance = 0.0

    if semester:
        # Get current semester enrolled hours
        from app.models.course import Course
        hours_result = await db.execute(
            select(func.sum(Course.credit_hours))
            .select_from(Enrollment)
            .join(TeachingUnit)
            .join(CourseOffering)
            .join(Course)
            .where(
                and_(
                    Enrollment.student_id == student.id,
                    Enrollment.semester_id == semester.id,
                    Enrollment.status == EnrollmentItemStatus.ENROLLED,
                )
            )
        )
        current_hours = hours_result.scalar() or 0

        # Get tuition balance
        from app.models.invoice import Invoice, InvoiceStatus
        balance_result = await db.execute(
            select(func.sum(Invoice.total_amount - Invoice.paid_amount))
            .where(
                and_(
                    Invoice.student_id == student.id,
                    Invoice.status.in_([InvoiceStatus.PENDING, InvoiceStatus.PARTIAL]),
                )
            )
        )
        tuition_balance = float(balance_result.scalar() or 0)

    return StudentDashboard(
        student_code=student.student_code,
        full_name=student.user.full_name,
        department=student.department.name,
        program=student.program.name,
        level=student.level,
        cgpa=float(student.cgpa),
        total_hours=student.total_hours,
        current_semester_hours=current_hours,
        academic_status=student.academic_status,
        enrollment_status=student.enrollment_status,
        tuition_balance=tuition_balance,
        warnings_count=len(student.academic_warnings),
    )


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(
    student_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get student by ID."""
    result = await db.execute(
        select(Student).where(Student.id == student_id)
    )
    student = result.scalar_one_or_none()
    if not student:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Student not found")
    return StudentResponse.model_validate(student)


@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: UUID,
    update_data: StudentUpdate,
    current_user: User = Depends(require_registrar),
    db: AsyncSession = Depends(get_db),
):
    """Update student profile. Requires registrar or admin role."""
    result = await db.execute(
        select(Student).where(Student.id == student_id)
    )
    student = result.scalar_one_or_none()
    if not student:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Student not found")

    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(student, key, value)

    await db.flush()
    return StudentResponse.model_validate(student)
