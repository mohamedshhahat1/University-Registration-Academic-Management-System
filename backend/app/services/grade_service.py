"""
Grade service - handles grading, GPA calculation, and academic warnings.
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.core.config import settings
from app.models.student import Student, AcademicStatus
from app.models.enrollment import Enrollment, EnrollmentItemStatus
from app.models.teaching_unit import TeachingUnit
from app.models.course_offering import CourseOffering
from app.models.course import Course
from app.models.grade import Grade
from app.models.semester_gpa import SemesterGPA
from app.models.academic_warning import AcademicWarning, WarningType
from app.schemas.grade import (
    GradeEntry,
    GPACalculationResult,
    TranscriptResponse,
    TranscriptEntry,
    SemesterGPAResponse,
)


# Grade scale mapping - using lower bounds for comparison
GRADE_SCALE = {
    "A+": {"min": 97, "max": 100, "points": 4.00},
    "A":  {"min": 93, "max": 96.99,  "points": 4.00},
    "A-": {"min": 90, "max": 92.99,  "points": 3.70},
    "B+": {"min": 87, "max": 89.99,  "points": 3.30},
    "B":  {"min": 83, "max": 86.99,  "points": 3.00},
    "B-": {"min": 80, "max": 82.99,  "points": 2.70},
    "C+": {"min": 77, "max": 79.99,  "points": 2.30},
    "C":  {"min": 73, "max": 76.99,  "points": 2.00},
    "C-": {"min": 70, "max": 72.99,  "points": 1.70},
    "D+": {"min": 67, "max": 69.99,  "points": 1.30},
    "D":  {"min": 60, "max": 66.99,  "points": 1.00},
    "F":  {"min": 0,  "max": 59.99,  "points": 0.00},
}


class GradeService:
    """Service for grading and GPA operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    def _score_to_letter(self, score: float) -> str:
        """Convert numeric score to letter grade."""
        for letter, info in GRADE_SCALE.items():
            if info["min"] <= score <= info["max"]:
                return letter
        return "F"

    def _letter_to_points(self, letter: str) -> float:
        """Convert letter grade to grade points."""
        return GRADE_SCALE.get(letter, {"points": 0.0})["points"]

    def _calculate_total_score(
        self,
        midterm1: Optional[float],
        midterm2: Optional[float],
        coursework: Optional[float],
        final_exam: Optional[float],
    ) -> Optional[float]:
        """
        Calculate weighted total score.
        Weights: Midterm 1 = 30%, Midterm 2 = 20%, Coursework = 10%, Final = 40%
        Returns None if any component is missing.
        """
        if any(v is None for v in [midterm1, midterm2, coursework, final_exam]):
            return None

        total = (
            midterm1 * settings.MIDTERM1_WEIGHT
            + midterm2 * settings.MIDTERM2_WEIGHT
            + coursework * settings.COURSEWORK_WEIGHT
            + final_exam * settings.FINAL_EXAM_WEIGHT
        )
        return round(total, 2)

    async def enter_grade(self, grade_entry: GradeEntry) -> Grade:
        """
        Enter or update grade components for an enrollment.
        Automatically calculates total score, letter grade, and grade points
        when all components are present.
        """
        # Get or create grade
        result = await self.db.execute(
            select(Grade).where(Grade.enrollment_id == grade_entry.enrollment_id)
        )
        grade = result.scalar_one_or_none()

        if not grade:
            grade = Grade(enrollment_id=grade_entry.enrollment_id)
            self.db.add(grade)

        # Update components (only if provided)
        if grade_entry.midterm1 is not None:
            grade.midterm1 = grade_entry.midterm1
        if grade_entry.midterm2 is not None:
            grade.midterm2 = grade_entry.midterm2
        if grade_entry.coursework is not None:
            grade.coursework = grade_entry.coursework
        if grade_entry.final_exam is not None:
            grade.final_exam = grade_entry.final_exam

        # Calculate total if all components present
        total = self._calculate_total_score(
            float(grade.midterm1) if grade.midterm1 is not None else None,
            float(grade.midterm2) if grade.midterm2 is not None else None,
            float(grade.coursework) if grade.coursework is not None else None,
            float(grade.final_exam) if grade.final_exam is not None else None,
        )

        if total is not None:
            grade.total_score = total
            grade.letter_grade = self._score_to_letter(total)
            grade.grade_points = self._letter_to_points(grade.letter_grade)

        await self.db.flush()
        return grade

    async def enter_bulk_grades(self, grades: List[GradeEntry]) -> List[Grade]:
        """Enter grades for multiple students at once."""
        results = []
        for entry in grades:
            grade = await self.enter_grade(entry)
            results.append(grade)
        return results

    async def calculate_semester_gpa(
        self, student_id: UUID, semester_id: UUID
    ) -> GPACalculationResult:
        """
        Calculate semester GPA and update cumulative GPA.
        
        GPA = sum(grade_points × credit_hours) / sum(credit_hours)
        Only includes completed courses with grades.
        """
        # Get all completed enrollments for this semester with grades
        result = await self.db.execute(
            select(Enrollment)
            .where(
                and_(
                    Enrollment.student_id == student_id,
                    Enrollment.semester_id == semester_id,
                    Enrollment.status == EnrollmentItemStatus.COMPLETED,
                )
            )
            .options(
                selectinload(Enrollment.grade),
                selectinload(Enrollment.teaching_unit)
                .selectinload(TeachingUnit.offering)
                .selectinload(CourseOffering.course),
            )
        )
        enrollments = result.scalars().all()

        semester_hours = 0
        semester_points = 0.0

        for enrollment in enrollments:
            if enrollment.grade and enrollment.grade.grade_points is not None:
                credit_hours = enrollment.teaching_unit.offering.course.credit_hours
                points = float(enrollment.grade.grade_points) * credit_hours
                semester_hours += credit_hours
                semester_points += points

        # Calculate semester GPA
        semester_gpa = round(semester_points / semester_hours, 2) if semester_hours > 0 else 0.0

        # Save or update semester GPA record
        gpa_result = await self.db.execute(
            select(SemesterGPA).where(
                and_(
                    SemesterGPA.student_id == student_id,
                    SemesterGPA.semester_id == semester_id,
                )
            )
        )
        sem_gpa = gpa_result.scalar_one_or_none()

        if not sem_gpa:
            sem_gpa = SemesterGPA(
                student_id=student_id,
                semester_id=semester_id,
                gpa=semester_gpa,
                total_hours=semester_hours,
                total_points=semester_points,
            )
            self.db.add(sem_gpa)
        else:
            sem_gpa.gpa = semester_gpa
            sem_gpa.total_hours = semester_hours
            sem_gpa.total_points = semester_points

        # Calculate cumulative GPA
        all_gpas_result = await self.db.execute(
            select(SemesterGPA).where(SemesterGPA.student_id == student_id)
        )
        all_gpas = all_gpas_result.scalars().all()

        total_hours = sum(g.total_hours for g in all_gpas)
        total_points = sum(float(g.total_points) for g in all_gpas)

        # Include current semester if not yet saved
        if not any(g.semester_id == semester_id for g in all_gpas):
            total_hours += semester_hours
            total_points += semester_points

        cgpa = round(total_points / total_hours, 2) if total_hours > 0 else 0.0

        # Update student CGPA and total hours
        student_result = await self.db.execute(
            select(Student).where(Student.id == student_id)
        )
        student = student_result.scalar_one()
        student.cgpa = cgpa
        student.total_hours = total_hours

        # Check for academic warning
        await self._check_academic_warning(student, semester_id, cgpa)

        await self.db.flush()

        return GPACalculationResult(
            semester_gpa=semester_gpa,
            cumulative_gpa=cgpa,
            semester_hours=semester_hours,
            total_hours=total_hours,
            semester_points=semester_points,
            total_points=total_points,
        )

    async def _check_academic_warning(
        self, student: Student, semester_id: UUID, cgpa: float
    ) -> None:
        """Check if student needs an academic warning (CGPA < 2.0)."""
        if cgpa < settings.ACADEMIC_WARNING_CGPA:
            # Count existing warnings
            warning_count_result = await self.db.execute(
                select(func.count(AcademicWarning.id)).where(
                    and_(
                        AcademicWarning.student_id == student.id,
                        AcademicWarning.type == WarningType.GPA_WARNING,
                    )
                )
            )
            warning_count = warning_count_result.scalar() or 0

            # Create new warning
            warning = AcademicWarning(
                student_id=student.id,
                semester_id=semester_id,
                type=WarningType.GPA_WARNING,
                reason=f"CGPA ({cgpa}) is below minimum threshold ({settings.ACADEMIC_WARNING_CGPA})",
                warning_number=warning_count + 1,
            )
            self.db.add(warning)

            # Update student academic status
            if warning_count + 1 >= 2:
                student.academic_status = AcademicStatus.PROBATION
            else:
                student.academic_status = AcademicStatus.WARNING
        else:
            # CGPA recovered - set back to good standing
            student.academic_status = AcademicStatus.GOOD_STANDING

    async def get_transcript(self, student_id: UUID) -> TranscriptResponse:
        """Generate full academic transcript for a student."""
        # Get student info
        student_result = await self.db.execute(
            select(Student)
            .where(Student.id == student_id)
            .options(
                selectinload(Student.user),
                selectinload(Student.department),
                selectinload(Student.program),
            )
        )
        student = student_result.scalar_one_or_none()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        # Get all completed enrollments with grades
        enrollments_result = await self.db.execute(
            select(Enrollment)
            .where(
                and_(
                    Enrollment.student_id == student_id,
                    Enrollment.status == EnrollmentItemStatus.COMPLETED,
                )
            )
            .options(
                selectinload(Enrollment.grade),
                selectinload(Enrollment.teaching_unit)
                .selectinload(TeachingUnit.offering)
                .selectinload(CourseOffering.course),
                selectinload(Enrollment.semester),
            )
        )
        enrollments = enrollments_result.scalars().all()

        # Build transcript entries
        entries = []
        for enrollment in enrollments:
            if enrollment.grade and enrollment.grade.letter_grade:
                course = enrollment.teaching_unit.offering.course
                entries.append(TranscriptEntry(
                    course_code=course.code,
                    course_name=course.name,
                    credit_hours=course.credit_hours,
                    letter_grade=enrollment.grade.letter_grade,
                    grade_points=float(enrollment.grade.grade_points),
                    semester_name=enrollment.semester.name,
                ))

        # Get semester GPAs
        gpas_result = await self.db.execute(
            select(SemesterGPA)
            .where(SemesterGPA.student_id == student_id)
            .options(selectinload(SemesterGPA.semester))
            .order_by(SemesterGPA.created_at)
        )
        gpas = gpas_result.scalars().all()

        semester_gpas = [
            SemesterGPAResponse(
                semester_name=g.semester.name,
                academic_year=g.semester.academic_year,
                gpa=float(g.gpa),
                total_hours=g.total_hours,
                total_points=float(g.total_points),
            )
            for g in gpas
        ]

        total_hours = sum(g.total_hours for g in gpas)
        total_points = sum(float(g.total_points) for g in gpas)

        return TranscriptResponse(
            student_code=student.student_code,
            student_name=student.user.full_name,
            department=student.department.name,
            program=student.program.name,
            entries=entries,
            semester_gpas=semester_gpas,
            cgpa=float(student.cgpa),
            total_hours=total_hours,
            total_points=total_points,
        )
