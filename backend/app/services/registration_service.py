"""
Registration service - handles course registration with validation.
Implements prerequisite checking, conflict detection, and credit hour limits.
"""

from typing import List, Optional
from uuid import UUID
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.core.config import settings
from app.models.student import Student
from app.models.semester import Semester
from app.models.course import Course
from app.models.course_offering import CourseOffering
from app.models.teaching_unit import TeachingUnit
from app.models.schedule import Schedule
from app.models.registration_cart import RegistrationCart, CartStatus
from app.models.registration_item import RegistrationItem
from app.models.advisor_approval import AdvisorApproval, ApprovalStatus
from app.models.enrollment import Enrollment, EnrollmentItemStatus
from app.models.grade import Grade
from app.models.prerequisite import Prerequisite
from app.schemas.registration import (
    ValidationError,
    RegistrationValidationResponse,
)


class RegistrationService:
    """Service for course registration operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    def _get_max_credit_hours(self, cgpa: float) -> int:
        """
        Get maximum allowed credit hours based on CGPA.
        
        Rules:
            CGPA >= 3.0  → 21 hours
            CGPA 2.0-2.99 → 18 hours
            CGPA 1.0-1.99 → 14 hours
            CGPA < 1.0   → 12 hours
        """
        if cgpa >= 3.0:
            return settings.MAX_CREDIT_HOURS_HIGH_GPA
        elif cgpa >= 2.0:
            return settings.MAX_CREDIT_HOURS_MID_GPA
        elif cgpa >= 1.0:
            return settings.MAX_CREDIT_HOURS_LOW_GPA
        else:
            return settings.MAX_CREDIT_HOURS_VERY_LOW_GPA

    async def get_or_create_cart(
        self, student_id: UUID, semester_id: UUID
    ) -> RegistrationCart:
        """Get existing draft cart or create a new one."""
        result = await self.db.execute(
            select(RegistrationCart)
            .where(
                and_(
                    RegistrationCart.student_id == student_id,
                    RegistrationCart.semester_id == semester_id,
                    RegistrationCart.status == CartStatus.DRAFT,
                )
            )
            .options(selectinload(RegistrationCart.items))
        )
        cart = result.scalar_one_or_none()

        if not cart:
            cart = RegistrationCart(
                student_id=student_id,
                semester_id=semester_id,
                status=CartStatus.DRAFT,
                total_hours=0,
            )
            self.db.add(cart)
            await self.db.flush()

        return cart

    async def add_to_cart(
        self, student_id: UUID, semester_id: UUID, teaching_unit_id: UUID
    ) -> RegistrationCart:
        """
        Add a teaching unit to the student's registration cart.
        Performs validation before adding.
        """
        # Verify registration period is open
        await self._validate_registration_period(semester_id)

        # Get or create cart
        cart = await self.get_or_create_cart(student_id, semester_id)

        if cart.status != CartStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cart is not in draft status. Cannot modify.",
            )

        # Get teaching unit with offering details
        result = await self.db.execute(
            select(TeachingUnit)
            .where(TeachingUnit.id == teaching_unit_id)
            .options(
                selectinload(TeachingUnit.offering).selectinload(CourseOffering.course),
                selectinload(TeachingUnit.schedules),
            )
        )
        unit = result.scalar_one_or_none()
        if not unit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Teaching unit not found",
            )

        # Check capacity
        if unit.current_enrolled >= unit.max_capacity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This class is full. No available seats.",
            )

        # Check if already in cart
        existing_item = await self.db.execute(
            select(RegistrationItem).where(
                and_(
                    RegistrationItem.cart_id == cart.id,
                    RegistrationItem.teaching_unit_id == teaching_unit_id,
                )
            )
        )
        if existing_item.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This teaching unit is already in your cart.",
            )

        # Add item to cart
        item = RegistrationItem(
            cart_id=cart.id,
            teaching_unit_id=teaching_unit_id,
        )
        self.db.add(item)

        # Update total hours
        cart.total_hours += unit.offering.course.credit_hours
        await self.db.flush()

        return cart

    async def remove_from_cart(
        self, student_id: UUID, semester_id: UUID, teaching_unit_id: UUID
    ) -> RegistrationCart:
        """Remove a teaching unit from the cart."""
        cart = await self.get_or_create_cart(student_id, semester_id)

        if cart.status != CartStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cart is not in draft status. Cannot modify.",
            )

        # Find the item
        result = await self.db.execute(
            select(RegistrationItem)
            .where(
                and_(
                    RegistrationItem.cart_id == cart.id,
                    RegistrationItem.teaching_unit_id == teaching_unit_id,
                )
            )
        )
        item = result.scalar_one_or_none()
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found in cart.",
            )

        # Get credit hours for the course
        unit_result = await self.db.execute(
            select(TeachingUnit)
            .where(TeachingUnit.id == teaching_unit_id)
            .options(selectinload(TeachingUnit.offering).selectinload(CourseOffering.course))
        )
        unit = unit_result.scalar_one()

        # Remove item and update hours
        await self.db.delete(item)
        cart.total_hours -= unit.offering.course.credit_hours
        await self.db.flush()

        return cart

    async def validate_cart(
        self, student_id: UUID, semester_id: UUID
    ) -> RegistrationValidationResponse:
        """
        Validate entire registration cart.
        Checks: prerequisites, schedule conflicts, credit limits, capacity.
        """
        errors: List[ValidationError] = []

        # Get student
        student_result = await self.db.execute(
            select(Student).where(Student.id == student_id)
        )
        student = student_result.scalar_one_or_none()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        # Get cart with items
        cart = await self.get_or_create_cart(student_id, semester_id)
        max_hours = self._get_max_credit_hours(float(student.cgpa))

        # 1. Credit hour limit validation
        if cart.total_hours > max_hours:
            errors.append(ValidationError(
                error_type="credit_limit",
                message=f"Total hours ({cart.total_hours}) exceeds maximum allowed ({max_hours}) based on your CGPA ({student.cgpa})",
                details={"total": cart.total_hours, "max": max_hours, "cgpa": float(student.cgpa)},
            ))

        # Get all teaching units in cart
        items_result = await self.db.execute(
            select(RegistrationItem)
            .where(RegistrationItem.cart_id == cart.id)
            .options(
                selectinload(RegistrationItem.teaching_unit)
                .selectinload(TeachingUnit.offering)
                .selectinload(CourseOffering.course),
                selectinload(RegistrationItem.teaching_unit)
                .selectinload(TeachingUnit.schedules),
            )
        )
        items = items_result.scalars().all()

        # 2. Prerequisite validation
        for item in items:
            course = item.teaching_unit.offering.course
            prereq_errors = await self._validate_prerequisites(
                student_id, course
            )
            errors.extend(prereq_errors)

        # 3. Schedule conflict detection
        conflict_errors = self._detect_schedule_conflicts(items)
        errors.extend(conflict_errors)

        # 4. Capacity validation
        for item in items:
            unit = item.teaching_unit
            if unit.current_enrolled >= unit.max_capacity:
                errors.append(ValidationError(
                    error_type="capacity",
                    message=f"No available seats in {unit.offering.course.code} ({unit.type.value} group {unit.group_number})",
                    course_code=unit.offering.course.code,
                ))

        return RegistrationValidationResponse(
            is_valid=len(errors) == 0,
            errors=errors,
            total_hours=cart.total_hours,
            max_allowed_hours=max_hours,
        )

    async def submit_cart(self, student_id: UUID, semester_id: UUID) -> RegistrationCart:
        """
        Submit cart for advisor approval.
        Validates cart before submission.
        """
        # Validate first
        validation = await self.validate_cart(student_id, semester_id)
        if not validation.is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Registration validation failed",
                    "errors": [e.model_dump() for e in validation.errors],
                },
            )

        cart = await self.get_or_create_cart(student_id, semester_id)
        if cart.status != CartStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cart is not in draft status.",
            )

        if cart.total_hours == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot submit empty cart.",
            )

        # Get student's advisor
        student_result = await self.db.execute(
            select(Student).where(Student.id == student_id)
        )
        student = student_result.scalar_one()

        # Update cart status
        from datetime import datetime
        cart.status = CartStatus.SUBMITTED
        cart.submitted_at = datetime.utcnow()

        # Create advisor approval record
        if student.advisor_id:
            approval = AdvisorApproval(
                cart_id=cart.id,
                advisor_id=student.advisor_id,
                status=ApprovalStatus.PENDING,
            )
            self.db.add(approval)

        await self.db.flush()
        return cart

    async def approve_cart(
        self, cart_id: UUID, advisor_id: UUID, comments: Optional[str] = None
    ) -> RegistrationCart:
        """Advisor approves a registration cart."""
        from datetime import datetime

        result = await self.db.execute(
            select(AdvisorApproval).where(AdvisorApproval.cart_id == cart_id)
        )
        approval = result.scalar_one_or_none()
        if not approval:
            raise HTTPException(status_code=404, detail="Approval record not found")

        if approval.advisor_id != advisor_id:
            raise HTTPException(status_code=403, detail="Not authorized to approve this cart")

        approval.status = ApprovalStatus.APPROVED
        approval.comments = comments
        approval.reviewed_at = datetime.utcnow()

        # Update cart status
        cart_result = await self.db.execute(
            select(RegistrationCart).where(RegistrationCart.id == cart_id)
        )
        cart = cart_result.scalar_one()
        cart.status = CartStatus.APPROVED

        await self.db.flush()
        return cart

    async def reject_cart(
        self, cart_id: UUID, advisor_id: UUID, comments: str
    ) -> RegistrationCart:
        """Advisor rejects a registration cart."""
        from datetime import datetime

        result = await self.db.execute(
            select(AdvisorApproval).where(AdvisorApproval.cart_id == cart_id)
        )
        approval = result.scalar_one_or_none()
        if not approval:
            raise HTTPException(status_code=404, detail="Approval record not found")

        if approval.advisor_id != advisor_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        approval.status = ApprovalStatus.REJECTED
        approval.comments = comments
        approval.reviewed_at = datetime.utcnow()

        # Update cart status
        cart_result = await self.db.execute(
            select(RegistrationCart).where(RegistrationCart.id == cart_id)
        )
        cart = cart_result.scalar_one()
        cart.status = CartStatus.REJECTED

        await self.db.flush()
        return cart

    async def confirm_enrollment(
        self, student_id: UUID, semester_id: UUID
    ) -> List[Enrollment]:
        """
        Convert approved cart items into actual enrollments.
        Called after payment is confirmed.
        """
        # Get approved cart
        result = await self.db.execute(
            select(RegistrationCart)
            .where(
                and_(
                    RegistrationCart.student_id == student_id,
                    RegistrationCart.semester_id == semester_id,
                    RegistrationCart.status == CartStatus.APPROVED,
                )
            )
            .options(selectinload(RegistrationCart.items))
        )
        cart = result.scalar_one_or_none()
        if not cart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No approved cart found for this semester",
            )

        enrollments = []
        for item in cart.items:
            # Create enrollment
            enrollment = Enrollment(
                student_id=student_id,
                teaching_unit_id=item.teaching_unit_id,
                semester_id=semester_id,
                status=EnrollmentItemStatus.ENROLLED,
            )
            self.db.add(enrollment)

            # Update teaching unit enrollment count
            unit_result = await self.db.execute(
                select(TeachingUnit).where(TeachingUnit.id == item.teaching_unit_id)
            )
            unit = unit_result.scalar_one()
            unit.current_enrolled += 1

            enrollments.append(enrollment)

        # Update cart status
        cart.status = CartStatus.ENROLLED
        await self.db.flush()

        return enrollments

    async def _validate_registration_period(self, semester_id: UUID) -> None:
        """Check if registration is currently open."""
        result = await self.db.execute(
            select(Semester).where(Semester.id == semester_id)
        )
        semester = result.scalar_one_or_none()
        if not semester:
            raise HTTPException(status_code=404, detail="Semester not found")

        today = date.today()
        if today < semester.registration_start or today > semester.registration_end:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Registration is not open. Period: {semester.registration_start} to {semester.registration_end}",
            )

    async def _validate_prerequisites(
        self, student_id: UUID, course: Course
    ) -> List[ValidationError]:
        """Check if student has passed all prerequisites."""
        errors = []

        # Get prerequisites for the course
        prereq_result = await self.db.execute(
            select(Prerequisite)
            .where(Prerequisite.course_id == course.id)
            .options(selectinload(Prerequisite.prerequisite_course))
        )
        prerequisites = prereq_result.scalars().all()

        for prereq in prerequisites:
            # Check if student has completed the prerequisite
            enrollment_result = await self.db.execute(
                select(Enrollment)
                .join(TeachingUnit)
                .join(CourseOffering)
                .where(
                    and_(
                        Enrollment.student_id == student_id,
                        CourseOffering.course_id == prereq.prerequisite_id,
                        Enrollment.status == EnrollmentItemStatus.COMPLETED,
                    )
                )
                .options(selectinload(Enrollment.grade))
            )
            enrollment = enrollment_result.scalar_one_or_none()

            if not enrollment:
                errors.append(ValidationError(
                    error_type="prerequisite",
                    message=f"Missing prerequisite: {prereq.prerequisite_course.code} - {prereq.prerequisite_course.name}",
                    course_code=course.code,
                    details={"prerequisite_code": prereq.prerequisite_course.code},
                ))
            elif enrollment.grade:
                # Check minimum grade
                grade_order = {
                    "A+": 12, "A": 11, "A-": 10,
                    "B+": 9, "B": 8, "B-": 7,
                    "C+": 6, "C": 5, "C-": 4,
                    "D+": 3, "D": 2, "F": 0,
                }
                student_grade_val = grade_order.get(enrollment.grade.letter_grade, 0)
                required_grade_val = grade_order.get(prereq.min_grade, 2)

                if student_grade_val < required_grade_val:
                    errors.append(ValidationError(
                        error_type="prerequisite",
                        message=f"Minimum grade {prereq.min_grade} required in {prereq.prerequisite_course.code}. You got {enrollment.grade.letter_grade}.",
                        course_code=course.code,
                        details={
                            "prerequisite_code": prereq.prerequisite_course.code,
                            "required_grade": prereq.min_grade,
                            "actual_grade": enrollment.grade.letter_grade,
                        },
                    ))

        return errors

    def _detect_schedule_conflicts(
        self, items: List[RegistrationItem]
    ) -> List[ValidationError]:
        """Detect time slot overlaps between selected courses."""
        errors = []
        schedules_list = []

        # Collect all schedules with course info
        for item in items:
            unit = item.teaching_unit
            course = unit.offering.course
            for schedule in unit.schedules:
                schedules_list.append({
                    "course_code": course.code,
                    "unit_type": unit.type.value,
                    "group": unit.group_number,
                    "day": schedule.day_of_week,
                    "start": schedule.start_time,
                    "end": schedule.end_time,
                })

        # Check all pairs for conflicts
        for i in range(len(schedules_list)):
            for j in range(i + 1, len(schedules_list)):
                s1 = schedules_list[i]
                s2 = schedules_list[j]

                if s1["day"] == s2["day"]:
                    # Check time overlap
                    if s1["start"] < s2["end"] and s2["start"] < s1["end"]:
                        errors.append(ValidationError(
                            error_type="conflict",
                            message=(
                                f"Schedule conflict: {s1['course_code']} ({s1['unit_type']}) "
                                f"overlaps with {s2['course_code']} ({s2['unit_type']}) "
                                f"on {s1['day'].value}"
                            ),
                            course_code=s1["course_code"],
                            details={
                                "course1": s1["course_code"],
                                "course2": s2["course_code"],
                                "day": s1["day"].value,
                            },
                        ))

        return errors
