"""
Authentication dependencies for FastAPI dependency injection.
Provides current user extraction and role-based access control.
"""

from typing import List
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.auth.security import decode_token
from app.models.user import User, UserRole


# Bearer token security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Extract and validate current user from JWT token.
    
    Raises:
        HTTPException 401: If token is invalid or user not found
        HTTPException 401: If user account is deactivated
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload is None:
        raise credentials_exception
    
    if payload.get("type") != "access":
        raise credentials_exception
    
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # Fetch user from database
    result = await db.execute(
        select(User).where(User.id == UUID(user_id))
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is deactivated",
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensure the current user is active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return current_user


class RoleChecker:
    """
    Role-based access control dependency.
    
    Usage:
        @router.get("/admin-only", dependencies=[Depends(RoleChecker([UserRole.ADMIN]))])
        async def admin_endpoint():
            ...
    """
    
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles
    
    async def __call__(
        self, current_user: User = Depends(get_current_user)
    ) -> User:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this resource",
            )
        return current_user


# Pre-configured role checkers for common access patterns
require_admin = RoleChecker([UserRole.ADMIN])
require_registrar = RoleChecker([UserRole.REGISTRAR, UserRole.ADMIN])
require_finance = RoleChecker([UserRole.FINANCE, UserRole.ADMIN])
require_instructor = RoleChecker([UserRole.INSTRUCTOR, UserRole.ADMIN])
require_advisor = RoleChecker([UserRole.ADVISOR, UserRole.ADMIN])
require_student = RoleChecker([UserRole.STUDENT])
