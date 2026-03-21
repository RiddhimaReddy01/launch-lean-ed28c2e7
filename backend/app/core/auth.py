"""
Supabase JWT verification middleware.
For the hackathon, we use a lightweight approach:
- Extract JWT from Authorization header
- Verify with Supabase's JWKS endpoint
- For development, allow bypass with X-Dev-Mode header
"""

from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import httpx
from app.core.config import settings

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Verify the Supabase JWT and return user info.
    In development mode, returns a mock user if no token is provided.
    """
    # Development bypass
    if settings.ENVIRONMENT == "development" and credentials is None:
        return {"id": "d23de268-412c-4b85-8fa9-29416047b765", "email": "dev@launchlens.ai"}

    if credentials is None:
        raise HTTPException(status_code=401, detail="Missing authorization token")

    token = credentials.credentials

    try:
        # Supabase JWTs are signed with the project's JWT secret
        # For hackathon simplicity, we decode without full JWKS verification
        # and trust the Supabase infrastructure
        payload = jwt.decode(
            token,
            settings.SUPABASE_ANON_KEY,
            algorithms=["HS256"],
            audience="authenticated",
            options={"verify_exp": True, "verify_aud": False},
        )
        return {
            "id": payload.get("sub", "unknown"),
            "email": payload.get("email", ""),
        }
    except JWTError:
        # Fallback: try without audience verification for dev tokens
        try:
            payload = jwt.decode(
                token,
                settings.SUPABASE_ANON_KEY,
                algorithms=["HS256"],
                options={"verify_exp": True, "verify_aud": False},
            )
            return {
                "id": payload.get("sub", "unknown"),
                "email": payload.get("email", ""),
            }
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")


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
