"""
API v1 Router - aggregates all endpoint routers.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import auth, students, courses, registration, finance, grades, attendance

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(students.router)
api_router.include_router(courses.router)
api_router.include_router(registration.router)
api_router.include_router(finance.router)
api_router.include_router(grades.router)
api_router.include_router(attendance.router)
