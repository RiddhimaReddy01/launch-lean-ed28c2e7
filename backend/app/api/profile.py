"""
User Profile API
GET  /api/profile - Get current user profile
PATCH /api/profile - Update user profile (display name, avatar)
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from supabase import create_client

from app.core.config import settings
from app.core.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


# ═══════════════════════════════════════════════════════════════
# SCHEMAS
# ═══════════════════════════════════════════════════════════════


class ProfileResponse(BaseModel):
    """User profile."""
    id: str
    email: str
    display_name: Optional[str]
    avatar_url: Optional[str]


class UpdateProfileRequest(BaseModel):
    """Request to update profile."""
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None


# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════


def get_supabase():
    """Get Supabase client."""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)


# ═══════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════


@router.get("/api/profile", response_model=ProfileResponse)
async def get_profile(
    user: dict = Depends(get_current_user),
):
    """Get current user profile."""
    logger.info(f"Fetching profile for user {user['id']}")

    supabase = get_supabase()

    try:
        # Fetch profile from public.profiles table
        response = supabase.table("profiles").select("*").eq("id", user["id"]).execute()

        if not response.data:
            # Profile doesn't exist yet, create default
            profile_data = {
                "id": user["id"],
                "email": user.get("email", ""),
                "display_name": user.get("user_metadata", {}).get("full_name", ""),
                "avatar_url": user.get("user_metadata", {}).get("avatar_url"),
            }
            logger.info(f"Creating default profile for {user['id']}")
            return ProfileResponse(**profile_data)

        profile_dict = response.data[0] if isinstance(response.data[0], dict) else dict(response.data[0])

        return ProfileResponse(
            id=str(profile_dict.get("id", "")),
            email=str(profile_dict.get("email", "")),
            display_name=profile_dict.get("display_name"),
            avatar_url=profile_dict.get("avatar_url"),
        )

    except Exception as e:
        logger.error(f"Failed to get profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to get profile")


@router.patch("/api/profile", response_model=ProfileResponse)
async def update_profile(
    req: UpdateProfileRequest,
    user: dict = Depends(get_current_user),
):
    """Update user profile."""
    logger.info(f"Updating profile for user {user['id']}")

    supabase = get_supabase()

    try:
        # Prepare update data
        update_data = {}
        if req.display_name is not None:
            update_data["display_name"] = req.display_name
        if req.avatar_url is not None:
            update_data["avatar_url"] = req.avatar_url

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        # First check if profile exists
        check_response = supabase.table("profiles").select("id").eq("id", user["id"]).execute()

        if check_response.data:
            # Update existing profile
            response = supabase.table("profiles").update(update_data).eq("id", user["id"]).execute()
        else:
            # Create new profile
            profile_data = {
                "id": user["id"],
                "email": user.get("email", ""),
                "display_name": req.display_name or user.get("user_metadata", {}).get("full_name", ""),
                "avatar_url": req.avatar_url or user.get("user_metadata", {}).get("avatar_url"),
            }
            response = supabase.table("profiles").insert(profile_data).execute()

        if not response.data:
            raise HTTPException(status_code=400, detail="Failed to update profile")

        profile_dict = response.data[0] if isinstance(response.data[0], dict) else dict(response.data[0])

        logger.info(f"Profile updated for {user['id']}")

        return ProfileResponse(
            id=str(profile_dict.get("id", "")),
            email=str(profile_dict.get("email", "")),
            display_name=profile_dict.get("display_name"),
            avatar_url=profile_dict.get("avatar_url"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to update profile")
