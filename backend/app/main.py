"""
University Registration & Academic Management System
Main FastAPI application entry point.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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

    # Serve Flutter web frontend from the same server
    frontend_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "frontend", "build", "web"
    )
    if os.path.exists(frontend_path):
        # Serve static assets (JS, CSS, images, etc.)
        app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "assets")), name="assets")
        app.mount("/icons", StaticFiles(directory=os.path.join(frontend_path, "icons")), name="icons")
        app.mount("/canvaskit", StaticFiles(directory=os.path.join(frontend_path, "canvaskit")), name="canvaskit")

        # Serve individual static files
        @app.get("/flutter.js")
        async def flutter_js():
            return FileResponse(os.path.join(frontend_path, "flutter.js"))

        @app.get("/flutter_bootstrap.js")
        async def flutter_bootstrap_js():
            return FileResponse(os.path.join(frontend_path, "flutter_bootstrap.js"))

        @app.get("/flutter_service_worker.js")
        async def flutter_sw():
            return FileResponse(os.path.join(frontend_path, "flutter_service_worker.js"))

        @app.get("/main.dart.js")
        async def main_dart_js():
            return FileResponse(os.path.join(frontend_path, "main.dart.js"))

        @app.get("/manifest.json")
        async def manifest():
            return FileResponse(os.path.join(frontend_path, "manifest.json"))

        @app.get("/version.json")
        async def version():
            return FileResponse(os.path.join(frontend_path, "version.json"))

        @app.get("/favicon.png")
        async def favicon():
            return FileResponse(os.path.join(frontend_path, "favicon.png"))

        # Catch-all: serve index.html for SPA routing
        @app.get("/{full_path:path}")
        async def serve_frontend(full_path: str):
            # Don't intercept API or docs routes
            if full_path.startswith("api/") or full_path in ["docs", "redoc", "openapi.json", "health"]:
                return None
            file_path = os.path.join(frontend_path, full_path)
            if os.path.isfile(file_path):
                return FileResponse(file_path)
            return FileResponse(os.path.join(frontend_path, "index.html"))

    return app


app = create_app()
