"""
SQLAlchemy ORM Models.
All models are imported here for Alembic auto-detection.
"""

from app.models.user import User
from app.models.department import Department
from app.models.program import Program
from app.models.student import Student
from app.models.instructor import Instructor
from app.models.semester import Semester
from app.models.course import Course
from app.models.prerequisite import Prerequisite
from app.models.course_offering import CourseOffering
from app.models.teaching_unit import TeachingUnit
from app.models.classroom import Classroom
from app.models.schedule import Schedule
from app.models.registration_cart import RegistrationCart
from app.models.registration_item import RegistrationItem
from app.models.advisor_approval import AdvisorApproval
from app.models.enrollment import Enrollment
from app.models.invoice import Invoice
from app.models.payment import Payment
from app.models.tuition_rate import TuitionRate
from app.models.grade import Grade
from app.models.semester_gpa import SemesterGPA
from app.models.attendance import Attendance
from app.models.academic_warning import AcademicWarning

__all__ = [
    "User",
    "Department",
    "Program",
    "Student",
    "Instructor",
    "Semester",
    "Course",
    "Prerequisite",
    "CourseOffering",
    "TeachingUnit",
    "Classroom",
    "Schedule",
    "RegistrationCart",
    "RegistrationItem",
    "AdvisorApproval",
    "Enrollment",
    "Invoice",
    "Payment",
    "TuitionRate",
    "Grade",
    "SemesterGPA",
    "Attendance",
    "AcademicWarning",
]
