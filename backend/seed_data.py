"""
Database seed script - populates the system with realistic test data.
Run: python seed_data.py
"""
import asyncio, sys
sys.path.insert(0, '.')

from app.core.database import init_db, AsyncSessionLocal
from app.models.user import User, UserRole
from app.models.department import Department
from app.models.program import Program
from app.models.student import Student, AcademicStatus
from app.models.instructor import Instructor
from app.models.semester import Semester, SemesterType
from app.models.course import Course
from app.models.prerequisite import Prerequisite
from app.models.course_offering import CourseOffering, OfferingStatus
from app.models.teaching_unit import TeachingUnit, TeachingUnitType
from app.models.schedule import Schedule, DayOfWeek
from app.models.classroom import Classroom, ClassroomType
from app.models.enrollment import Enrollment, EnrollmentItemStatus
from app.models.invoice import Invoice, InvoiceStatus
from app.models.payment import Payment, PaymentMethod, PaymentStatus
from app.models.tuition_rate import TuitionRate
from app.models.attendance import Attendance, AttendanceStatus
from app.models.academic_warning import AcademicWarning, WarningType
from app.models.registration_cart import RegistrationCart, CartStatus
from app.models.registration_item import RegistrationItem
from app.models.advisor_approval import AdvisorApproval, ApprovalStatus
from app.auth.security import hash_password
from app.schemas.grade import GradeEntry
from app.services.grade_service import GradeService
from datetime import date, time, datetime


async def seed():
    await init_db()
    async with AsyncSessionLocal() as db:
        # === USERS ===
        admin = User(email='admin@university.edu', hashed_password=hash_password('admin123'),
            full_name='Dr. Ahmed Hassan', phone='01000000001', role=UserRole.ADMIN)
        registrar = User(email='registrar@university.edu', hashed_password=hash_password('reg123'),
            full_name='Eng. Fatma Ali', role=UserRole.REGISTRAR)
        finance_user = User(email='finance@university.edu', hashed_password=hash_password('fin123'),
            full_name='Mr. Karim Nasser', role=UserRole.FINANCE)
        advisor1 = User(email='dr.omar@university.edu', hashed_password=hash_password('advisor123'),
            full_name='Dr. Omar Mostafa', role=UserRole.ADVISOR)
        instr1 = User(email='dr.sara@university.edu', hashed_password=hash_password('instr123'),
            full_name='Dr. Sara Ibrahim', role=UserRole.INSTRUCTOR)
        instr2 = User(email='dr.ali@university.edu', hashed_password=hash_password('instr123'),
            full_name='Dr. Ali Mahmoud', role=UserRole.INSTRUCTOR)
        instr3 = User(email='dr.mona@university.edu', hashed_password=hash_password('instr123'),
            full_name='Dr. Mona Khaled', role=UserRole.INSTRUCTOR)
        stud1 = User(email='mohamed.shahat@student.edu', hashed_password=hash_password('student123'),
            full_name='Mohamed Shahat', phone='01112345678', role=UserRole.STUDENT)
        stud2 = User(email='ahmed.salem@student.edu', hashed_password=hash_password('student123'),
            full_name='Ahmed Salem', role=UserRole.STUDENT)
        stud3 = User(email='yasmin.hassan@student.edu', hashed_password=hash_password('student123'),
            full_name='Yasmin Hassan', role=UserRole.STUDENT)
        stud4 = User(email='omar.fathy@student.edu', hashed_password=hash_password('student123'),
            full_name='Omar Fathy', role=UserRole.STUDENT)
        stud5 = User(email='nour.ahmed@student.edu', hashed_password=hash_password('student123'),
            full_name='Nour Ahmed', role=UserRole.STUDENT)
        db.add_all([admin, registrar, finance_user, advisor1, instr1, instr2, instr3,
                    stud1, stud2, stud3, stud4, stud5])
        await db.flush()

        # === DEPARTMENTS & PROGRAMS ===
        dept_ce = Department(name='Computer Engineering', code='CE', head_id=instr1.id)
        dept_ee = Department(name='Electronics Engineering', code='EE', head_id=instr2.id)
        dept_math = Department(name='Mathematics & Physics', code='MP', head_id=instr3.id)
        db.add_all([dept_ce, dept_ee, dept_math])
        await db.flush()
        prog_ce = Program(name='BSc Computer Engineering', code='BSCE', department_id=dept_ce.id, total_hours=160)
        prog_ee = Program(name='BSc Electronics Engineering', code='BSEE', department_id=dept_ee.id, total_hours=160)
        db.add_all([prog_ce, prog_ee])
        await db.flush()

        # === INSTRUCTORS ===
        inst_rec1 = Instructor(user_id=instr1.id, department_id=dept_ce.id,
            specialization='Artificial Intelligence', academic_rank='Associate Professor')
        inst_rec2 = Instructor(user_id=instr2.id, department_id=dept_ee.id,
            specialization='Digital Systems', academic_rank='Professor')
        inst_rec3 = Instructor(user_id=instr3.id, department_id=dept_math.id,
            specialization='Applied Mathematics', academic_rank='Lecturer')
        db.add_all([inst_rec1, inst_rec2, inst_rec3])
        await db.flush()

        # === SEMESTERS ===
        sem_prev = Semester(name='Spring 2025', type=SemesterType.SPRING, academic_year='2024/2025',
            start_date=date(2025,2,1), end_date=date(2025,6,15),
            registration_start=date(2025,1,15), registration_end=date(2025,1,30),
            add_drop_end=date(2025,2,15), withdrawal_end=date(2025,4,15), is_current=False)
        sem_current = Semester(name='Fall 2025', type=SemesterType.FALL, academic_year='2025/2026',
            start_date=date(2025,9,15), end_date=date(2026,1,15),
            registration_start=date(2025,8,1), registration_end=date(2026,9,10),
            add_drop_end=date(2025,9,25), withdrawal_end=date(2025,11,15), is_current=True)
        db.add_all([sem_prev, sem_current])
        await db.flush()

        # === STUDENTS ===
        student1 = Student(user_id=stud1.id, student_code='CE-2023-001', department_id=dept_ce.id,
            program_id=prog_ce.id, advisor_id=advisor1.id, admission_year=2023, level=3,
            cgpa=3.52, total_hours=65, academic_status=AcademicStatus.GOOD_STANDING)
        student2 = Student(user_id=stud2.id, student_code='CE-2023-002', department_id=dept_ce.id,
            program_id=prog_ce.id, advisor_id=advisor1.id, admission_year=2023, level=3,
            cgpa=2.85, total_hours=58)
        student3 = Student(user_id=stud3.id, student_code='CE-2024-001', department_id=dept_ce.id,
            program_id=prog_ce.id, advisor_id=advisor1.id, admission_year=2024, level=2,
            cgpa=3.91, total_hours=34)
        student4 = Student(user_id=stud4.id, student_code='EE-2023-001', department_id=dept_ee.id,
            program_id=prog_ee.id, advisor_id=advisor1.id, admission_year=2023, level=3,
            cgpa=1.85, total_hours=50, academic_status=AcademicStatus.WARNING)
        student5 = Student(user_id=stud5.id, student_code='CE-2024-002', department_id=dept_ce.id,
            program_id=prog_ce.id, advisor_id=advisor1.id, admission_year=2024, level=2,
            cgpa=3.15, total_hours=30)
        db.add_all([student1, student2, student3, student4, student5])
        await db.flush()

        # === COURSES ===
        courses_data = [
            ('CS101', 'Introduction to Programming', 3, dept_ce.id, True, True, True),
            ('CS201', 'Data Structures & Algorithms', 3, dept_ce.id, True, True, False),
            ('CS301', 'Database Systems', 3, dept_ce.id, True, True, True),
            ('CS302', 'Operating Systems', 3, dept_ce.id, True, True, False),
            ('CS401', 'Software Engineering', 3, dept_ce.id, True, True, False),
            ('CS402', 'Artificial Intelligence', 3, dept_ce.id, True, True, True),
            ('CS403', 'Computer Networks', 3, dept_ce.id, True, True, True),
            ('EE201', 'Digital Logic Design', 3, dept_ee.id, True, True, True),
            ('EE301', 'Microprocessors', 3, dept_ee.id, True, True, True),
            ('MATH101', 'Calculus I', 3, dept_math.id, True, True, False),
            ('MATH201', 'Calculus II', 3, dept_math.id, True, True, False),
            ('MATH301', 'Linear Algebra', 3, dept_math.id, True, True, False),
            ('PHYS101', 'Physics I', 3, dept_math.id, True, True, True),
            ('PHYS201', 'Physics II', 3, dept_math.id, True, True, True),
        ]
        course_objs = {}
        for code, name, hours, dept_id, lec, sec, lab in courses_data:
            c = Course(code=code, name=name, credit_hours=hours, department_id=dept_id,
                has_lecture=lec, has_section=sec, has_lab=lab)
            db.add(c)
            course_objs[code] = c
        await db.flush()

        # === PREREQUISITES ===
        for course_code, prereq_code, min_grade in [
            ('CS201','CS101','D'), ('CS301','CS201','C'), ('CS302','CS201','C'),
            ('CS401','CS301','C'), ('CS402','CS201','C'), ('CS402','MATH301','D'),
            ('CS403','CS302','D'), ('EE301','EE201','D'), ('MATH201','MATH101','D'),
            ('MATH301','MATH201','D'), ('PHYS201','PHYS101','D'),
        ]:
            db.add(Prerequisite(course_id=course_objs[course_code].id,
                prerequisite_id=course_objs[prereq_code].id, min_grade=min_grade))
        await db.flush()

        # === CLASSROOMS ===
        room_objs = {}
        for name, building, cap, rtype in [
            ('Hall A','Building 1',200,ClassroomType.LECTURE_HALL),
            ('Hall B','Building 1',150,ClassroomType.LECTURE_HALL),
            ('Room 101','Building 2',40,ClassroomType.TUTORIAL_ROOM),
            ('Room 102','Building 2',40,ClassroomType.TUTORIAL_ROOM),
            ('Lab 1','Building 3',30,ClassroomType.LAB),
            ('Lab 2','Building 3',30,ClassroomType.LAB),
        ]:
            r = Classroom(name=name, building=building, capacity=cap, type=rtype)
            db.add(r)
            room_objs[name] = r
        await db.flush()

        # === TUITION RATES ===
        db.add_all([
            TuitionRate(academic_year='2023/2024', cost_per_hour=450.0, fixed_fees=1800.0),
            TuitionRate(academic_year='2024/2025', cost_per_hour=500.0, fixed_fees=2000.0),
            TuitionRate(academic_year='2025/2026', cost_per_hour=550.0, fixed_fees=2200.0),
        ])
        await db.flush()

        # === COURSE OFFERINGS & SCHEDULES (Current Semester) ===
        offering_courses = ['CS201','CS301','CS302','CS402','CS403','EE301','MATH201','MATH301']
        offerings, units = {}, {}
        instructor_map = {'CS201':inst_rec1,'CS301':inst_rec1,'CS302':inst_rec1,
            'CS402':inst_rec1,'CS403':inst_rec2,'EE301':inst_rec2,'MATH201':inst_rec3,'MATH301':inst_rec3}
        schedule_map = {
            'CS201': [(DayOfWeek.SUNDAY,time(8,0),time(9,30),'Hall A'),(DayOfWeek.TUESDAY,time(8,0),time(9,30),'Hall A')],
            'CS301': [(DayOfWeek.SUNDAY,time(10,0),time(11,30),'Hall B'),(DayOfWeek.WEDNESDAY,time(10,0),time(11,30),'Hall B')],
            'CS302': [(DayOfWeek.MONDAY,time(8,0),time(9,30),'Hall A'),(DayOfWeek.WEDNESDAY,time(8,0),time(9,30),'Hall A')],
            'CS402': [(DayOfWeek.MONDAY,time(10,0),time(11,30),'Hall B'),(DayOfWeek.THURSDAY,time(10,0),time(11,30),'Hall B')],
            'CS403': [(DayOfWeek.TUESDAY,time(10,0),time(11,30),'Hall A'),(DayOfWeek.THURSDAY,time(8,0),time(9,30),'Hall A')],
            'EE301': [(DayOfWeek.SUNDAY,time(12,0),time(13,30),'Hall A'),(DayOfWeek.TUESDAY,time(12,0),time(13,30),'Hall A')],
            'MATH201': [(DayOfWeek.MONDAY,time(12,0),time(13,30),'Hall B'),(DayOfWeek.WEDNESDAY,time(12,0),time(13,30),'Hall B')],
            'MATH301': [(DayOfWeek.SUNDAY,time(14,0),time(15,30),'Hall B'),(DayOfWeek.THURSDAY,time(12,0),time(13,30),'Hall B')],
        }
        for code in offering_courses:
            o = CourseOffering(course_id=course_objs[code].id, semester_id=sem_current.id,
                max_capacity=120, current_enrolled=0, status=OfferingStatus.OPEN)
            db.add(o)
            offerings[code] = o
        await db.flush()
        for code in offering_courses:
            u = TeachingUnit(offering_id=offerings[code].id, type=TeachingUnitType.LECTURE,
                group_number=1, instructor_id=instructor_map[code].id, max_capacity=120, current_enrolled=0)
            db.add(u)
            units[code] = u
        await db.flush()
        for code, slots in schedule_map.items():
            for day, start, end, room_name in slots:
                db.add(Schedule(teaching_unit_id=units[code].id, day_of_week=day,
                    start_time=start, end_time=end, classroom_id=room_objs[room_name].id))
        await db.flush()

        # === PREVIOUS SEMESTER DATA (Student1 grades) ===
        grade_service = GradeService(db)
        for code, m1, m2, cw, final in [('CS101',88,92,95,85),('MATH101',75,80,70,78),
                                          ('PHYS101',90,85,88,92),('EE201',82,78,85,80)]:
            po = CourseOffering(course_id=course_objs[code].id, semester_id=sem_prev.id,
                max_capacity=100, current_enrolled=30, status=OfferingStatus.CLOSED)
            db.add(po); await db.flush()
            pu = TeachingUnit(offering_id=po.id, type=TeachingUnitType.LECTURE,
                group_number=1, instructor_id=inst_rec1.id, max_capacity=100, current_enrolled=30)
            db.add(pu); await db.flush()
            e = Enrollment(student_id=student1.id, teaching_unit_id=pu.id,
                semester_id=sem_prev.id, status=EnrollmentItemStatus.COMPLETED)
            db.add(e); await db.flush()
            await grade_service.enter_grade(GradeEntry(enrollment_id=e.id, midterm1=m1, midterm2=m2, coursework=cw, final_exam=final))
        await grade_service.calculate_semester_gpa(student1.id, sem_prev.id)

        # === CURRENT SEMESTER ENROLLMENTS ===
        for code in ['CS201','CS301','MATH201']:
            db.add(Enrollment(student_id=student1.id, teaching_unit_id=units[code].id,
                semester_id=sem_current.id, status=EnrollmentItemStatus.ENROLLED))
            offerings[code].current_enrolled += 1; units[code].current_enrolled += 1
        await db.flush()

        # === INVOICE & PAYMENT ===
        total = (9*450+1800)*0.9  # 9hrs, 2023 rate, 10% scholarship
        inv = Invoice(student_id=student1.id, semester_id=sem_current.id,
            credit_hours_cost=9*450, fixed_fees=1800, scholarship_discount=(9*450+1800)*0.1,
            total_amount=total, paid_amount=3000, status=InvoiceStatus.PARTIAL, due_date=date(2025,10,1))
        db.add(inv); await db.flush()
        db.add(Payment(invoice_id=inv.id, amount=3000, payment_method=PaymentMethod.VISA,
            transaction_ref='VISA-2025-8876', status=PaymentStatus.COMPLETED, paid_at=datetime(2025,9,5)))
        await db.flush()

        # === ATTENDANCE ===
        from sqlalchemy import select
        cs201_enr = (await db.execute(select(Enrollment).where(
            Enrollment.student_id==student1.id, Enrollment.teaching_unit_id==units['CS201'].id))).scalar_one()
        for d, s in [(date(2025,9,15),AttendanceStatus.PRESENT),(date(2025,9,17),AttendanceStatus.PRESENT),
            (date(2025,9,22),AttendanceStatus.PRESENT),(date(2025,9,24),AttendanceStatus.ABSENT),
            (date(2025,9,29),AttendanceStatus.PRESENT),(date(2025,10,1),AttendanceStatus.PRESENT),
            (date(2025,10,6),AttendanceStatus.EXCUSED),(date(2025,10,8),AttendanceStatus.PRESENT),
            (date(2025,10,13),AttendanceStatus.PRESENT),(date(2025,10,15),AttendanceStatus.ABSENT)]:
            db.add(Attendance(enrollment_id=cs201_enr.id, teaching_unit_id=units['CS201'].id, date=d, status=s))
        await db.flush()

        # === PENDING CART (Student4) ===
        cart = RegistrationCart(student_id=student4.id, semester_id=sem_current.id,
            status=CartStatus.SUBMITTED, total_hours=9, submitted_at=datetime(2025,8,28,14,0))
        db.add(cart); await db.flush()
        for code in ['EE301','MATH201','MATH301']:
            db.add(RegistrationItem(cart_id=cart.id, teaching_unit_id=units[code].id))
        await db.flush()
        db.add(AdvisorApproval(cart_id=cart.id, advisor_id=advisor1.id, status=ApprovalStatus.PENDING))
        db.add(AcademicWarning(student_id=student4.id, semester_id=sem_prev.id,
            type=WarningType.GPA_WARNING, reason='CGPA (1.85) below minimum (2.0)', warning_number=1))
        
        await db.commit()
        print("✅ Database seeded successfully!")


if __name__ == '__main__':
    asyncio.run(seed())
