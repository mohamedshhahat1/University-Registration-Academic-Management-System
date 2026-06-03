"""
Registration API endpoints.
Handles course registration cart, validation, and advisor approval.
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.auth.dependencies import get_current_user, require_advisor, require_student
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.semester import Semester
from app.models.course_offering import CourseOffering
from app.models.teaching_unit import TeachingUnit
from app.models.registration_cart import RegistrationCart, CartStatus
from app.models.advisor_approval import AdvisorApproval, ApprovalStatus
from app.services.registration_service import RegistrationService
from app.schemas.registration import (
    CourseOfferingResponse,
    TeachingUnitWithSchedule,
    TeachingUnitResponse,
    ScheduleResponse,
    AddToCartRequest,
    RemoveFromCartRequest,
    RegistrationCartResponse,
    RegistrationItemResponse,
    RegistrationValidationResponse,
    ApprovalDecisionRequest,
    ApprovalResponse,
)

router = APIRouter(prefix="/registration", tags=["Registration"])


@router.get("/offerings", response_model=List[CourseOfferingResponse])
async def list_course_offerings(
    semester_id: UUID = None,
    department_id: UUID = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List available course offerings for registration."""
    query = select(CourseOffering).options(
        selectinload(CourseOffering.course),
        selectinload(CourseOffering.semester),
    )

    if semester_id:
        query = query.where(CourseOffering.semester_id == semester_id)
    else:
        # Default to current semester
        current_sem = await db.execute(
            select(Semester).where(Semester.is_current == True)
        )
        semester = current_sem.scalar_one_or_none()
        if semester:
            query = query.where(CourseOffering.semester_id == semester.id)

    if department_id:
        from app.models.course import Course
        query = query.join(Course).where(Course.department_id == department_id)

    result = await db.execute(query)
    offerings = result.scalars().all()

    return [
        CourseOfferingResponse(
            id=o.id,
            course_id=o.course_id,
            course_code=o.course.code,
            course_name=o.course.name,
            credit_hours=o.course.credit_hours,
            semester_id=o.semester_id,
            max_capacity=o.max_capacity,
            current_enrolled=o.current_enrolled,
            available_seats=o.max_capacity - o.current_enrolled,
            status=o.status.value,
        )
        for o in offerings
    ]


@router.get("/offerings/{offering_id}/units", response_model=List[TeachingUnitWithSchedule])
async def get_offering_units(
    offering_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get teaching units (lecture/section/lab) for a course offering."""
    result = await db.execute(
        select(TeachingUnit)
        .where(TeachingUnit.offering_id == offering_id)
        .options(
            selectinload(TeachingUnit.schedules),
            selectinload(TeachingUnit.instructor).selectinload(lambda: None),
        )
    )
    units = result.scalars().all()

    response = []
    for unit in units:
        schedules = [
            ScheduleResponse(
                id=s.id,
                day_of_week=s.day_of_week,
                start_time=s.start_time,
                end_time=s.end_time,
                classroom_name=None,
                building=None,
            )
            for s in unit.schedules
        ]
        response.append(TeachingUnitWithSchedule(
            unit=TeachingUnitResponse(
                id=unit.id,
                offering_id=unit.offering_id,
                type=unit.type,
                group_number=unit.group_number,
                instructor_name=None,
                max_capacity=unit.max_capacity,
                current_enrolled=unit.current_enrolled,
                available_seats=unit.max_capacity - unit.current_enrolled,
            ),
            schedules=schedules,
        ))

    return response


@router.get("/cart", response_model=RegistrationCartResponse)
async def get_my_cart(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current student's registration cart."""
    # Get student
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

    service = RegistrationService(db)
    cart = await service.get_or_create_cart(student.id, semester.id)

    # Load items with details
    items_result = await db.execute(
        select(RegistrationCart)
        .where(RegistrationCart.id == cart.id)
        .options(
            selectinload(RegistrationCart.items)
            .selectinload(lambda: None)
        )
    )

    return RegistrationCartResponse(
        id=cart.id,
        student_id=cart.student_id,
        semester_id=cart.semester_id,
        status=cart.status,
        total_hours=cart.total_hours,
        items=[],
        submitted_at=cart.submitted_at,
        created_at=cart.created_at,
    )


@router.post("/cart/add")
async def add_to_cart(
    request: AddToCartRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a teaching unit to registration cart."""
    student_result = await db.execute(
        select(Student).where(Student.user_id == current_user.id)
    )
    student = student_result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    sem_result = await db.execute(
        select(Semester).where(Semester.is_current == True)
    )
    semester = sem_result.scalar_one_or_none()
    if not semester:
        raise HTTPException(status_code=404, detail="No current semester")

    service = RegistrationService(db)
    cart = await service.add_to_cart(student.id, semester.id, request.teaching_unit_id)
    return {"message": "Course added to cart", "total_hours": cart.total_hours}


@router.post("/cart/remove")
async def remove_from_cart(
    request: RemoveFromCartRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a teaching unit from registration cart."""
    student_result = await db.execute(
        select(Student).where(Student.user_id == current_user.id)
    )
    student = student_result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    sem_result = await db.execute(
        select(Semester).where(Semester.is_current == True)
    )
    semester = sem_result.scalar_one_or_none()
    if not semester:
        raise HTTPException(status_code=404, detail="No current semester")

    service = RegistrationService(db)
    cart = await service.remove_from_cart(student.id, semester.id, request.teaching_unit_id)
    return {"message": "Course removed from cart", "total_hours": cart.total_hours}


@router.post("/cart/validate", response_model=RegistrationValidationResponse)
async def validate_cart(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Validate registration cart (check prerequisites, conflicts, limits)."""
    student_result = await db.execute(
        select(Student).where(Student.user_id == current_user.id)
    )
    student = student_result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    sem_result = await db.execute(
        select(Semester).where(Semester.is_current == True)
    )
    semester = sem_result.scalar_one_or_none()
    if not semester:
        raise HTTPException(status_code=404, detail="No current semester")

    service = RegistrationService(db)
    return await service.validate_cart(student.id, semester.id)


@router.post("/cart/submit")
async def submit_cart(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit registration cart for advisor approval."""
    student_result = await db.execute(
        select(Student).where(Student.user_id == current_user.id)
    )
    student = student_result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    sem_result = await db.execute(
        select(Semester).where(Semester.is_current == True)
    )
    semester = sem_result.scalar_one_or_none()
    if not semester:
        raise HTTPException(status_code=404, detail="No current semester")

    service = RegistrationService(db)
    cart = await service.submit_cart(student.id, semester.id)
    return {"message": "Cart submitted for approval", "status": cart.status.value}


# ============ ADVISOR APPROVAL ENDPOINTS ============

@router.get("/approvals/pending", response_model=List[ApprovalResponse])
async def get_pending_approvals(
    current_user: User = Depends(require_advisor),
    db: AsyncSession = Depends(get_db),
):
    """Get pending registration approvals for the advisor."""
    result = await db.execute(
        select(AdvisorApproval)
        .where(
            and_(
                AdvisorApproval.advisor_id == current_user.id,
                AdvisorApproval.status == ApprovalStatus.PENDING,
            )
        )
    )
    approvals = result.scalars().all()
    return [
        ApprovalResponse(
            id=a.id,
            cart_id=a.cart_id,
            advisor_id=a.advisor_id,
            status=a.status,
            comments=a.comments,
            reviewed_at=a.reviewed_at,
        )
        for a in approvals
    ]


@router.post("/approvals/{cart_id}/decide")
async def decide_approval(
    cart_id: UUID,
    decision: ApprovalDecisionRequest,
    current_user: User = Depends(require_advisor),
    db: AsyncSession = Depends(get_db),
):
    """Approve or reject a registration cart."""
    service = RegistrationService(db)

    if decision.status == ApprovalStatus.APPROVED:
        await service.approve_cart(cart_id, current_user.id, decision.comments)
        return {"message": "Registration approved"}
    elif decision.status == ApprovalStatus.REJECTED:
        if not decision.comments:
            raise HTTPException(
                status_code=400, detail="Comments required for rejection"
            )
        await service.reject_cart(cart_id, current_user.id, decision.comments)
        return {"message": "Registration rejected"}
    else:
        raise HTTPException(status_code=400, detail="Invalid decision status")
