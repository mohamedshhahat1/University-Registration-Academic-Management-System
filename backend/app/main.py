"""
University Registration & Academic Management System
Main FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "A comprehensive university registration and academic management system. "
            "Supports course registration with prerequisite validation, schedule conflict detection, "
            "GPA-based credit limits, advisor approval workflow, tuition management with "
            "cohort-based pricing and scholarship engine, grading with automatic GPA calculation, "
            "and attendance tracking with academic warnings."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API router
    app.include_router(api_router)

    # Startup event - create tables
    @app.on_event("startup")
    async def startup():
        from app.core.database import init_db
        await init_db()

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "version": settings.APP_VERSION,
            "service": "University Registration System",
        }

    return app


app = create_app()
