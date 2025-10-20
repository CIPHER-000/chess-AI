"""Authentication middleware for FastAPI."""
from typing import Optional
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from loguru import logger

from ..services.auth_service import auth_service

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> dict:
    """
    Dependency to get current authenticated user.
    
    Extracts JWT token from Authorization header and validates it.
    
    Args:
        credentials: HTTP Bearer token from request header
    
    Returns:
        User data dict
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing"
        )
    
    token = credentials.credentials
    
    try:
        user = await auth_service.get_user(token)
        
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token"
            )
        
        return user
    
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Authentication failed"
        )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security, auto_error=False)
) -> Optional[dict]:
    """
    Optional authentication dependency.
    
    Returns user if authenticated, None otherwise.
    Doesn't raise exception for missing/invalid tokens.
    
    Args:
        credentials: Optional HTTP Bearer token
    
    Returns:
        User data dict or None
    """
    if not credentials:
        return None
    
    try:
        user = await auth_service.get_user(credentials.credentials)
        return user
    except Exception as e:
        logger.warning(f"Optional auth failed: {str(e)}")
        return None
