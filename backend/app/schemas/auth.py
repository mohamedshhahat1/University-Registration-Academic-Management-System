"""
Authentication schemas - request/response models for auth endpoints.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from app.models.user import UserRole


class LoginRequest(BaseModel):
    """Login credentials."""
    email: EmailStr
    password: str = Field(..., min_length=6)


class TokenResponse(BaseModel):
    """JWT token pair response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Request to refresh access token."""
    refresh_token: str


class RegisterRequest(BaseModel):
    """User registration request."""
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: Optional[str] = None
    national_id: Optional[str] = None
    role: UserRole


class UserResponse(BaseModel):
    """User information response."""
    id: UUID
    email: str
    full_name: str
    phone: Optional[str] = None
    national_id: Optional[str] = None
    role: UserRole
    is_active: bool

    class Config:
        from_attributes = True


class PasswordResetRequest(BaseModel):
    """Password reset request."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation with new password."""
    token: str
    new_password: str = Field(..., min_length=6)


class ChangePasswordRequest(BaseModel):
    """Change password for authenticated user."""
    current_password: str
    new_password: str = Field(..., min_length=6)
