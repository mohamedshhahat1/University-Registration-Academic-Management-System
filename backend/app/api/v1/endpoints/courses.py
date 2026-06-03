"""
Course API endpoints.
Handles course and semester management.
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.auth.dependencies import get_current_user, require_registrar
from app.models.user import User
from app.models.course import Course
from app.models.prerequisite import Prerequisite
from app.models.semester import Semester
from app.models.department import Department
from app.schemas.course import (
    CourseCreate,
    CourseUpdate,
    CourseResponse,
    PrerequisiteCreate,
    PrerequisiteResponse,
    CourseWithPrerequisites,
)
from app.schemas.semester import (
    SemesterCreate,
    SemesterUpdate,
    SemesterResponse,
)

router = APIRouter(tags=["Courses & Semesters"])


# ============ COURSE ENDPOINTS ============

@router.post("/courses", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    course_data: CourseCreate,
    current_user: User = Depends(require_registrar),
    db: AsyncSession = Depends(get_db),
):
    """Create a new course. Requires registrar or admin role."""
    # Check unique code
    existing = await db.execute(
        select(Course).where(Course.code == course_data.code)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Course code already exists")

    course = Course(**course_data.model_dump())
    db.add(course)
    await db.flush()
    return CourseResponse.model_validate(course)


@router.get("/courses", response_model=List[CourseResponse])
async def list_courses(
    department_id: UUID = None,
    active_only: bool = True,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all courses. Supports filtering by department."""
    query = select(Course)
    if department_id:
        query = query.where(Course.department_id == department_id)
    if active_only:
        query = query.where(Course.is_active == True)
    
    result = await db.execute(query.order_by(Course.code))
    return [CourseResponse.model_validate(c) for c in result.scalars().all()]


@router.get("/courses/{course_id}", response_model=CourseWithPrerequisites)
async def get_course(
    course_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get course details with prerequisites."""
    result = await db.execute(
        select(Course)
        .where(Course.id == course_id)
        .options(
            selectinload(Course.prerequisites)
            .selectinload(Prerequisite.prerequisite_course)
        )
    )
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    prereqs = [
        PrerequisiteResponse(
            id=p.id,
            course_id=p.course_id,
            prerequisite_id=p.prerequisite_id,
            prerequisite_code=p.prerequisite_course.code,
            prerequisite_name=p.prerequisite_course.name,
            min_grade=p.min_grade,
        )
        for p in course.prerequisites
    ]

    return CourseWithPrerequisites(
        course=CourseResponse.model_validate(course),
        prerequisites=prereqs,
    )


@router.put("/courses/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: UUID,
    update_data: CourseUpdate,
    current_user: User = Depends(require_registrar),
    db: AsyncSession = Depends(get_db),
):
    """Update course details. Requires registrar or admin role."""
    result = await db.execute(
        select(Course).where(Course.id == course_id)
    )
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(course, key, value)

    await db.flush()
    return CourseResponse.model_validate(course)


@router.post("/courses/{course_id}/prerequisites", response_model=PrerequisiteResponse)
async def add_prerequisite(
    course_id: UUID,
    prereq_data: PrerequisiteCreate,
    current_user: User = Depends(require_registrar),
    db: AsyncSession = Depends(get_db),
):
    """Add a prerequisite to a course."""
    # Verify both courses exist
    course = await db.execute(select(Course).where(Course.id == course_id))
    if not course.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Course not found")

    prereq_course_result = await db.execute(
        select(Course).where(Course.id == prereq_data.prerequisite_id)
    )
    prereq_course = prereq_course_result.scalar_one_or_none()
    if not prereq_course:
        raise HTTPException(status_code=404, detail="Prerequisite course not found")

    # Prevent self-reference
    if course_id == prereq_data.prerequisite_id:
        raise HTTPException(status_code=400, detail="Course cannot be its own prerequisite")

    # Check duplicate
    existing = await db.execute(
        select(Prerequisite).where(
            Prerequisite.course_id == course_id,
            Prerequisite.prerequisite_id == prereq_data.prerequisite_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Prerequisite already exists")

    prereq = Prerequisite(
        course_id=course_id,
        prerequisite_id=prereq_data.prerequisite_id,
        min_grade=prereq_data.min_grade,
    )
    db.add(prereq)
    await db.flush()

    return PrerequisiteResponse(
        id=prereq.id,
        course_id=prereq.course_id,
        prerequisite_id=prereq.prerequisite_id,
        prerequisite_code=prereq_course.code,
        prerequisite_name=prereq_course.name,
        min_grade=prereq.min_grade,
    )


# ============ SEMESTER ENDPOINTS ============

@router.post("/semesters", response_model=SemesterResponse, status_code=status.HTTP_201_CREATED)
async def create_semester(
    semester_data: SemesterCreate,
    current_user: User = Depends(require_registrar),
    db: AsyncSession = Depends(get_db),
):
    """Create a new semester. Requires registrar or admin role."""
    semester = Semester(**semester_data.model_dump())
    db.add(semester)
    await db.flush()
    return SemesterResponse.model_validate(semester)


@router.get("/semesters", response_model=List[SemesterResponse])
async def list_semesters(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all semesters."""
    result = await db.execute(
        select(Semester).order_by(Semester.start_date.desc())
    )
    return [SemesterResponse.model_validate(s) for s in result.scalars().all()]


@router.get("/semesters/current", response_model=SemesterResponse)
async def get_current_semester(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the current active semester."""
    result = await db.execute(
        select(Semester).where(Semester.is_current == True)
    )
    semester = result.scalar_one_or_none()
    if not semester:
        raise HTTPException(status_code=404, detail="No current semester set")
    return SemesterResponse.model_validate(semester)


@router.put("/semesters/{semester_id}", response_model=SemesterResponse)
async def update_semester(
    semester_id: UUID,
    update_data: SemesterUpdate,
    current_user: User = Depends(require_registrar),
    db: AsyncSession = Depends(get_db),
):
    """Update semester details."""
    result = await db.execute(
        select(Semester).where(Semester.id == semester_id)
    )
    semester = result.scalar_one_or_none()
    if not semester:
        raise HTTPException(status_code=404, detail="Semester not found")

    update_dict = update_data.model_dump(exclude_unset=True)

    # If setting as current, unset other current semesters
    if update_dict.get("is_current") is True:
        from sqlalchemy import update
        await db.execute(
            update(Semester).where(Semester.id != semester_id).values(is_current=False)
        )

    for key, value in update_dict.items():
        setattr(semester, key, value)

    await db.flush()
    return SemesterResponse.model_validate(semester)


# ============ DEPARTMENT ENDPOINTS ============

@router.get("/departments")
async def list_departments(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all departments."""
    result = await db.execute(
        select(Department).order_by(Department.name)
    )
    departments = result.scalars().all()
    return [
        {"id": d.id, "name": d.name, "code": d.code}
        for d in departments
    ]
