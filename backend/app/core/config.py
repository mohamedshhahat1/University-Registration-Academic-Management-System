"""
Application configuration settings.
Uses pydantic-settings to load from environment variables.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "University Registration & Academic Management System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/university_db"
    DATABASE_ECHO: bool = False

    # JWT Authentication
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    ALLOWED_ORIGINS: List[str] = ["*"]

    # Registration Rules
    MAX_CREDIT_HOURS_HIGH_GPA: int = 21  # CGPA >= 3.0
    MAX_CREDIT_HOURS_MID_GPA: int = 18   # CGPA 2.0-2.99
    MAX_CREDIT_HOURS_LOW_GPA: int = 14   # CGPA 1.0-1.99
    MAX_CREDIT_HOURS_VERY_LOW_GPA: int = 12  # CGPA < 1.0

    # Scholarship Rules
    SCHOLARSHIP_HIGH_DISCOUNT: float = 0.20  # CGPA >= 3.7 → 20%
    SCHOLARSHIP_MID_DISCOUNT: float = 0.10   # CGPA >= 3.3 → 10%
    SCHOLARSHIP_HIGH_THRESHOLD: float = 3.7
    SCHOLARSHIP_MID_THRESHOLD: float = 3.3

    # Grade Components Weights
    MIDTERM1_WEIGHT: float = 0.30
    MIDTERM2_WEIGHT: float = 0.20
    COURSEWORK_WEIGHT: float = 0.10
    FINAL_EXAM_WEIGHT: float = 0.40

    # Academic Warning Threshold
    ACADEMIC_WARNING_CGPA: float = 2.0

    # Attendance
    MIN_ATTENDANCE_PERCENTAGE: float = 75.0

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
