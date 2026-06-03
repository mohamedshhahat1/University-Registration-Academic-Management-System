# University Registration & Academic Management System

A comprehensive university registration and academic management system built with **FastAPI** (Backend) and **Flutter Web** (Frontend).

## 🏗️ System Architecture

- **Backend**: FastAPI + PostgreSQL + SQLAlchemy + Alembic
- **Frontend**: Flutter Web
- **Authentication**: JWT with Role-Based Access Control (RBAC)
- **Deployment**: Docker + Nginx

## 👥 User Roles

| Role | Responsibilities |
|------|-----------------|
| **Student** | Register courses, view schedule, view grades, pay tuition |
| **Academic Advisor** | Approve registrations, monitor performance, approve overloads |
| **Instructor** | Manage attendance, enter grades, view enrolled students |
| **Registrar** | Manage semesters, course offerings, registration periods |
| **Finance** | Manage invoices, record payments, generate reports |
| **Admin** | Full system access |

## 📋 Features

### Registration System
- GPA-based credit hour limits
- Prerequisite validation
- Schedule conflict detection
- Advisor approval workflow
- Registration deadlines & Add/Drop periods

### Finance System
- Credit-hour tuition calculation
- Cohort-based pricing (admission year rate)
- GPA-based scholarships
- Multiple payment methods (Cash, Visa, Fawry, Instapay)

### Academic Records
- Attendance tracking with automatic warnings
- Grade components (Midterm 1: 30%, Midterm 2: 20%, Coursework: 10%, Final: 40%)
- GPA/CGPA calculation
- Academic warning system (CGPA < 2.0)

### Credit Hour Limits (Based on CGPA)
| CGPA Range | Max Credit Hours |
|-----------|-----------------|
| ≥ 3.0 | 21 |
| 2.0 - 2.99 | 18 |
| 1.0 - 1.99 | 14 |
| < 1.0 | 12 |

### Scholarship Discounts
| CGPA Range | Discount |
|-----------|----------|
| ≥ 3.7 | 20% |
| ≥ 3.3 | 10% |

## 🚀 Getting Started

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
flutter pub get
flutter run -d chrome
```

## 📁 Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   ├── repositories/ # Data access layer
│   │   ├── auth/         # Authentication & RBAC
│   │   ├── utils/        # Utility functions
│   │   └── core/         # Configuration & settings
│   ├── migrations/       # Alembic migrations
│   └── tests/            # Unit & integration tests
│
├── frontend/
│   └── lib/
│       ├── core/         # Constants, theme, services, utils
│       ├── features/     # Feature modules
│       ├── shared/       # Shared widgets, models, providers
│       └── main.dart
│
├── docs/                 # Documentation & ERD
└── docker-compose.yml    # Docker configuration
```

## 📊 Development Phases

1. ✅ Database Design (ERD)
2. 🔨 Backend APIs
3. 🔨 Authentication
4. 🔨 Registration Module
5. 🔨 Finance Module
6. 🔨 Grades Module
7. 🔨 Flutter UI

## 📄 License

MIT License
