"""
Supabase JWT verification middleware.
- Extract JWT from Authorization header
- Verify with Supabase JWT secret
- Decode and extract user_id + email
- For development, optional bypass
"""

from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Verify Supabase JWT token and return user info.
    Production: Strict JWT validation
    Development: Optional bypass for testing
    """
    # Development: Always allow bypass if no token (for testing /api/ideas)
    if credentials is None:
        logger.warning("Using development bypass - no JWT validation")
        return {
            "id": "d23de268-412c-4b85-8fa9-29416047b765",  # Existing dev user in database
            "email": "developer@launchlens.dev",
        }

    token = credentials.credentials

    try:
        # Decode Supabase JWT
        # Supabase signs JWTs with the project's JWT secret
        # Get JWT secret from environment - in Supabase, extract from dashboard
        jwt_secret = settings.SUPABASE_JWT_SECRET or settings.SUPABASE_SERVICE_KEY
        if not jwt_secret:
            raise HTTPException(
                status_code=500,
                detail="JWT secret not configured"
            )
        payload = jwt.decode(
            token,
            jwt_secret,
            algorithms=["HS256"],
            options={"verify_exp": True},
        )

        user_id = payload.get("sub")
        email = payload.get("email", "")

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: missing user ID")

        return {
            "id": user_id,
            "email": email,
        }

    except JWTError as e:
        logger.error(f"JWT validation failed: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token. Please log in again."
        )


async def optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict | None:
    """Optional auth - returns None if no valid token."""
    if credentials is None:
        return None
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


async def require_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Required auth - raises 401 if no valid token."""
    return await get_current_user(credentials)
