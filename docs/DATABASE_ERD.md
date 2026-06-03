# Database Entity-Relationship Design (ERD)

## Overview

This document defines the complete database schema for the University Registration & Academic Management System.

---

## Core Entities

### 1. Users & Authentication

```
┌─────────────────────────────┐
│          users               │
├─────────────────────────────┤
│ id              UUID PK      │
│ email           VARCHAR(255)  │
│ hashed_password VARCHAR(255)  │
│ full_name       VARCHAR(255)  │
│ phone           VARCHAR(20)   │
│ national_id     VARCHAR(20)   │
│ role            ENUM          │
│ is_active       BOOLEAN       │
│ created_at      TIMESTAMP     │
│ updated_at      TIMESTAMP     │
└─────────────────────────────┘

Roles: student, advisor, instructor, registrar, finance, admin
```

### 2. Departments & Programs

```
┌─────────────────────────────┐
│        departments           │
├─────────────────────────────┤
│ id              UUID PK      │
│ name            VARCHAR(255)  │
│ code            VARCHAR(10)   │
│ head_id         UUID FK→users │
│ created_at      TIMESTAMP     │
└─────────────────────────────┘

┌─────────────────────────────┐
│          programs            │
├─────────────────────────────┤
│ id              UUID PK      │
│ name            VARCHAR(255)  │
│ code            VARCHAR(10)   │
│ department_id   UUID FK       │
│ total_hours     INTEGER       │
│ created_at      TIMESTAMP     │
└─────────────────────────────┘
```

### 3. Students

```
┌──────────────────────────────────┐
│            students               │
├──────────────────────────────────┤
│ id               UUID PK         │
│ user_id          UUID FK→users   │
│ student_code     VARCHAR(20)     │
│ department_id    UUID FK         │
│ program_id       UUID FK         │
│ advisor_id       UUID FK→users   │
│ admission_year   INTEGER         │
│ level            INTEGER         │
│ cgpa             DECIMAL(3,2)    │
│ total_hours      INTEGER         │
│ academic_status  ENUM            │
│ enrollment_status ENUM           │
│ created_at       TIMESTAMP       │
│ updated_at       TIMESTAMP       │
└──────────────────────────────────┘

Academic Status: good_standing, warning, probation, dismissed
Enrollment Status: active, suspended, graduated, withdrawn
```

### 4. Instructors

```
┌──────────────────────────────────┐
│           instructors             │
├──────────────────────────────────┤
│ id               UUID PK         │
│ user_id          UUID FK→users   │
│ department_id    UUID FK         │
│ specialization   VARCHAR(255)    │
│ academic_rank    VARCHAR(50)     │
│ created_at       TIMESTAMP       │
└──────────────────────────────────┘
```

### 5. Semesters

```
┌──────────────────────────────────┐
│           semesters               │
├──────────────────────────────────┤
│ id               UUID PK         │
│ name             VARCHAR(50)     │
│ type             ENUM            │
│ academic_year    VARCHAR(9)      │
│ start_date       DATE            │
│ end_date         DATE            │
│ registration_start DATE          │
│ registration_end   DATE          │
│ add_drop_end     DATE            │
│ withdrawal_end   DATE            │
│ is_current       BOOLEAN         │
│ created_at       TIMESTAMP       │
└──────────────────────────────────┘

Type: fall, spring, summer
```

### 6. Courses

```
┌──────────────────────────────────┐
│            courses                │
├──────────────────────────────────┤
│ id               UUID PK         │
│ code             VARCHAR(10)     │
│ name             VARCHAR(255)    │
│ description      TEXT            │
│ credit_hours     INTEGER         │
│ department_id    UUID FK         │
│ has_lecture      BOOLEAN         │
│ has_section      BOOLEAN         │
│ has_lab          BOOLEAN         │
│ is_active        BOOLEAN         │
│ created_at       TIMESTAMP       │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│         prerequisites             │
├──────────────────────────────────┤
│ id               UUID PK         │
│ course_id        UUID FK→courses │
│ prerequisite_id  UUID FK→courses │
│ min_grade        VARCHAR(2)      │
│ created_at       TIMESTAMP       │
└──────────────────────────────────┘
```

### 7. Course Offerings & Schedules

```
┌──────────────────────────────────┐
│        course_offerings           │
├──────────────────────────────────┤
│ id               UUID PK         │
│ course_id        UUID FK         │
│ semester_id      UUID FK         │
│ max_capacity     INTEGER         │
│ current_enrolled INTEGER         │
│ status           ENUM            │
│ created_at       TIMESTAMP       │
└──────────────────────────────────┘

Status: open, closed, cancelled

┌──────────────────────────────────┐
│        teaching_units             │
├──────────────────────────────────┤
│ id               UUID PK         │
│ offering_id      UUID FK         │
│ type             ENUM            │
│ group_number     INTEGER         │
│ instructor_id    UUID FK         │
│ max_capacity     INTEGER         │
│ current_enrolled INTEGER         │
│ created_at       TIMESTAMP       │
└──────────────────────────────────┘

Type: lecture, section, lab

┌──────────────────────────────────┐
│          schedules                │
├──────────────────────────────────┤
│ id               UUID PK         │
│ teaching_unit_id UUID FK         │
│ day_of_week      ENUM            │
│ start_time       TIME            │
│ end_time         TIME            │
│ classroom_id     UUID FK         │
│ created_at       TIMESTAMP       │
└──────────────────────────────────┘

Day: sunday, monday, tuesday, wednesday, thursday

┌──────────────────────────────────┐
│          classrooms               │
├──────────────────────────────────┤
│ id               UUID PK         │
│ name             VARCHAR(50)     │
│ building         VARCHAR(100)    │
│ capacity         INTEGER         │
│ type             ENUM            │
│ created_at       TIMESTAMP       │
└──────────────────────────────────┘

Type: lecture_hall, lab, tutorial_room
```

### 8. Registration System

```
┌──────────────────────────────────┐
│       registration_carts          │
├──────────────────────────────────┤
│ id               UUID PK         │
│ student_id       UUID FK         │
│ semester_id      UUID FK         │
│ status           ENUM            │
│ total_hours      INTEGER         │
│ submitted_at     TIMESTAMP       │
│ created_at       TIMESTAMP       │
│ updated_at       TIMESTAMP       │
└──────────────────────────────────┘

Status: draft, submitted, approved, rejected, enrolled

┌──────────────────────────────────┐
│       registration_items          │
├──────────────────────────────────┤
│ id               UUID PK         │
│ cart_id          UUID FK         │
│ teaching_unit_id UUID FK         │
│ created_at       TIMESTAMP       │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│      advisor_approvals            │
├──────────────────────────────────┤
│ id               UUID PK         │
│ cart_id          UUID FK         │
│ advisor_id       UUID FK→users   │
│ status           ENUM            │
│ comments         TEXT            │
│ reviewed_at      TIMESTAMP       │
│ created_at       TIMESTAMP       │
└──────────────────────────────────┘

Status: pending, approved, rejected
```

### 9. Enrollments

```
┌──────────────────────────────────┐
│         enrollments               │
├──────────────────────────────────┤
│ id               UUID PK         │
│ student_id       UUID FK         │
│ teaching_unit_id UUID FK         │
│ semester_id      UUID FK         │
│ status           ENUM            │
│ created_at       TIMESTAMP       │
│ updated_at       TIMESTAMP       │
└──────────────────────────────────┘

Status: enrolled, dropped, withdrawn, completed
```

### 10. Finance System

```
┌──────────────────────────────────┐
│           invoices                │
├──────────────────────────────────┤
│ id               UUID PK         │
│ student_id       UUID FK         │
│ semester_id      UUID FK         │
│ credit_hours_cost DECIMAL(10,2)  │
│ fixed_fees       DECIMAL(10,2)   │
│ scholarship_discount DECIMAL(10,2)│
│ total_amount     DECIMAL(10,2)   │
│ paid_amount      DECIMAL(10,2)   │
│ status           ENUM            │
│ due_date         DATE            │
│ created_at       TIMESTAMP       │
│ updated_at       TIMESTAMP       │
└──────────────────────────────────┘

Status: draft, pending, partial, paid, cancelled

┌──────────────────────────────────┐
│           payments                │
├──────────────────────────────────┤
│ id               UUID PK         │
│ invoice_id       UUID FK         │
│ amount           DECIMAL(10,2)   │
│ payment_method   ENUM            │
│ transaction_ref  VARCHAR(100)    │
│ status           ENUM            │
│ paid_at          TIMESTAMP       │
│ created_at       TIMESTAMP       │
└──────────────────────────────────┘

Payment Method: cash, visa, fawry, instapay
Status: pending, completed, failed, refunded

┌──────────────────────────────────┐
│        tuition_rates              │
├──────────────────────────────────┤
│ id               UUID PK         │
│ academic_year    VARCHAR(9)      │
│ cost_per_hour    DECIMAL(10,2)   │
│ fixed_fees       DECIMAL(10,2)   │
│ created_at       TIMESTAMP       │
└──────────────────────────────────┘
```

### 11. Grades & GPA

```
┌──────────────────────────────────┐
│            grades                 │
├──────────────────────────────────┤
│ id               UUID PK         │
│ enrollment_id    UUID FK         │
│ midterm1         DECIMAL(5,2)    │
│ midterm2         DECIMAL(5,2)    │
│ coursework       DECIMAL(5,2)    │
│ final_exam       DECIMAL(5,2)    │
│ total_score      DECIMAL(5,2)    │
│ letter_grade     VARCHAR(2)      │
│ grade_points     DECIMAL(3,2)    │
│ created_at       TIMESTAMP       │
│ updated_at       TIMESTAMP       │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│       semester_gpas               │
├──────────────────────────────────┤
│ id               UUID PK         │
│ student_id       UUID FK         │
│ semester_id      UUID FK         │
│ gpa              DECIMAL(3,2)    │
│ total_hours      INTEGER         │
│ total_points     DECIMAL(7,2)    │
│ created_at       TIMESTAMP       │
└──────────────────────────────────┘
```

### 12. Attendance

```
┌──────────────────────────────────┐
│          attendance               │
├──────────────────────────────────┤
│ id               UUID PK         │
│ enrollment_id    UUID FK         │
│ teaching_unit_id UUID FK         │
│ date             DATE            │
│ status           ENUM            │
│ notes            TEXT            │
│ created_at       TIMESTAMP       │
└──────────────────────────────────┘

Status: present, absent, excused
```

### 13. Academic Warnings

```
┌──────────────────────────────────┐
│      academic_warnings            │
├──────────────────────────────────┤
│ id               UUID PK         │
│ student_id       UUID FK         │
│ semester_id      UUID FK         │
│ type             ENUM            │
│ reason           TEXT            │
│ warning_number   INTEGER         │
│ created_at       TIMESTAMP       │
└──────────────────────────────────┘

Type: gpa_warning, attendance_warning, probation
```

---

## Relationships Diagram

```
Users ─────┬──── Students ────── Departments
           │         │                │
           │         ├── Programs ────┘
           │         │
           ├──── Instructors ─── Departments
           │
           └──── (Advisors = Users with advisor role)

Courses ──── Prerequisites (self-referencing)
    │
    └── Course Offerings ──── Semesters
              │
              └── Teaching Units ──── Schedules ──── Classrooms
                       │
                       └── Enrollments ──── Students
                              │
                              ├── Grades
                              └── Attendance

Students ──── Registration Carts ──── Registration Items ──── Teaching Units
                     │
                     └── Advisor Approvals

Students ──── Invoices ──── Payments
                │
                └── Tuition Rates (by admission year)

Students ──── Semester GPAs
Students ──── Academic Warnings
```

---

## Indexes

### Performance Indexes
- `users.email` (UNIQUE)
- `students.student_code` (UNIQUE)
- `students.user_id` (UNIQUE)
- `courses.code` (UNIQUE)
- `enrollments.(student_id, semester_id)`
- `grades.enrollment_id` (UNIQUE)
- `schedules.(teaching_unit_id, day_of_week)`
- `attendance.(enrollment_id, date)`
- `invoices.(student_id, semester_id)`

---

## Grade Scale

| Letter | Points | Score Range |
|--------|--------|-------------|
| A+     | 4.00   | 97-100      |
| A      | 4.00   | 93-96       |
| A-     | 3.70   | 90-92       |
| B+     | 3.30   | 87-89       |
| B      | 3.00   | 83-86       |
| B-     | 2.70   | 80-82       |
| C+     | 2.30   | 77-79       |
| C      | 2.00   | 73-76       |
| C-     | 1.70   | 70-72       |
| D+     | 1.30   | 67-69       |
| D      | 1.00   | 60-66       |
| F      | 0.00   | 0-59        |
