"""
POST /api/ideas - Save idea with all research
GET  /api/ideas - List user's saved ideas
GET  /api/ideas/{idea_id} - Retrieve specific idea
PATCH /api/ideas/{idea_id} - Update idea sections
DELETE /api/ideas/{idea_id} - Delete idea
"""

import logging
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from supabase import create_client

from app.core.config import settings
from app.core.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


# ═══════════════════════════════════════════════════════════════
# SCHEMAS (Request/Response Models)
# ═══════════════════════════════════════════════════════════════

class SaveIdeaRequest(BaseModel):
    """Request to save a new idea."""
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    decomposition: Optional[dict] = None
    discover: Optional[dict] = None
    analyze: Optional[dict] = None
    setup: Optional[dict] = None
    validation: Optional[dict] = None
    tags: Optional[list[str]] = None
    notes: Optional[str] = None


class UpdateIdeaRequest(BaseModel):
    """Request to update an idea."""
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None
    decomposition: Optional[dict] = None
    discover: Optional[dict] = None
    analyze: Optional[dict] = None
    setup: Optional[dict] = None
    validate: Optional[dict] = None
    swot: Optional[dict] = None
    risks: Optional[dict] = None
    financials: Optional[dict] = None
    pricing: Optional[dict] = None
    acquisition: Optional[dict] = None
    tags: Optional[list[str]] = None
    notes: Optional[str] = None


class IdeaResponse(BaseModel):
    """Response model for idea data."""
    id: str
    title: str
    description: Optional[str]
    status: str
    created_at: str
    updated_at: str
    has_decompose: bool = False
    has_discover: bool = False
    has_analyze: bool = False
    has_setup: bool = False
    has_validate: bool = False
    tags: list[str] = []


class IdeaDetailResponse(BaseModel):
    """Full idea with all research data."""
    id: str
    title: str
    description: Optional[str]
    status: str
    decomposition: Optional[dict] = None
    discover: Optional[dict] = None
    analyze: Optional[dict] = None
    setup: Optional[dict] = None
    validation: Optional[dict] = None
    swot: Optional[dict] = None
    risks: Optional[dict] = None
    financials: Optional[dict] = None
    pricing: Optional[dict] = None
    acquisition: Optional[dict] = None
    tags: list[str] = []
    notes: Optional[str] = None
    created_at: str
    updated_at: str


# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def get_supabase():
    """Get Supabase client."""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)


def _check_progress(idea: dict) -> dict:
    """Check which modules have been completed."""
    return {
        "has_decompose": idea.get("decomposition") is not None,
        "has_discover": idea.get("discover") is not None,
        "has_analyze": idea.get("analyze") is not None,
        "has_setup": idea.get("setup") is not None,
        "has_validate": idea.get("validate") is not None,
    }


# ═══════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@router.post("/api/ideas", response_model=IdeaResponse)
async def save_idea(
    req: SaveIdeaRequest,
    user: dict = Depends(get_current_user),
):
    """Save a new idea with all research data."""

    logger.info(f"User {user['id']} saving idea: {req.title}")

    supabase = get_supabase()

    # Prepare data
    idea_data = {
        "user_id": user["id"],
        "title": req.title,
        "description": req.description,
        "decomposition": req.decomposition,
        "discover": req.discover,
        "analyze": req.analyze,
        "setup": req.setup,
        "validate": req.validation,
        "tags": req.tags or [],
        "notes": req.notes,
        "status": "draft",
    }

    try:
        # Insert into Supabase
        response = supabase.table("ideas").insert(idea_data).execute()

        if not response.data:
            raise HTTPException(status_code=400, detail="Failed to save idea")

        # Convert Supabase response to clean dict
        raw_idea = response.data[0]
        if isinstance(raw_idea, dict):
            idea_dict = raw_idea
        else:
            idea_dict = dict(raw_idea)

        logger.info(f"Idea saved with ID: {idea_dict.get('id')}")

        progress = _check_progress(idea_dict)

        return IdeaResponse(
            id=str(idea_dict.get("id", "")),
            title=str(idea_dict.get("title", "")),
            description=idea_dict.get("description"),
            status=str(idea_dict.get("status", "draft")),
            created_at=str(idea_dict.get("created_at", "")),
            updated_at=str(idea_dict.get("updated_at", "")),
            tags=list(idea_dict.get("tags", [])),
            **progress
        )

    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        logger.error(f"Error saving idea: {error_msg}", exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)


@router.get("/api/ideas", response_model=list[IdeaResponse])
async def list_ideas(
    user: dict = Depends(get_current_user),
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
):
    """List all user's saved ideas."""

    logger.info(f"User {user['id']} listing ideas")

    supabase = get_supabase()

    try:
        # Build query
        query = supabase.table("ideas")\
            .select("id, title, description, status, created_at, updated_at, tags, decomposition, discover, analyze, setup, validate")\
            .eq("user_id", user["id"])

        # Filter by status if provided
        if status:
            query = query.eq("status", status)

        # Order by most recent first
        query = query.order("updated_at", desc=True)

        # Pagination
        query = query.range(skip, skip + limit - 1)

        # Execute
        response = query.execute()

        ideas = []
        for idea in response.data:
            ideas.append(IdeaResponse(
                id=idea["id"],
                title=idea["title"],
                description=idea["description"],
                status=idea["status"],
                created_at=idea["created_at"],
                updated_at=idea["updated_at"],
                tags=idea.get("tags", []),
                **_check_progress(idea)
            ))

        logger.info(f"Found {len(ideas)} ideas for user {user['id']}")

        return ideas

    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        logger.error(f"Error listing ideas: {error_msg}", exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)


@router.get("/api/ideas/{idea_id}", response_model=IdeaDetailResponse)
async def get_idea(
    idea_id: str,
    user: dict = Depends(get_current_user),
):
    """Retrieve full idea with all research data."""

    logger.info(f"User {user['id']} retrieving idea {idea_id}")

    supabase = get_supabase()

    try:
        # Get idea from database
        response = supabase.table("ideas")\
            .select("*")\
            .eq("id", idea_id)\
            .eq("user_id", user["id"])\
            .single()\
            .execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Idea not found")

        idea = response.data

        return IdeaDetailResponse(
            id=idea["id"],
            title=idea["title"],
            description=idea["description"],
            status=idea["status"],
            decomposition=idea.get("decomposition"),
            discover=idea.get("discover"),
            analyze=idea.get("analyze"),
            setup=idea.get("setup"),
            validation=idea.get("validate"),
            swot=idea.get("swot"),
            risks=idea.get("risks"),
            financials=idea.get("financials"),
            pricing=idea.get("pricing"),
            acquisition=idea.get("acquisition"),
            tags=idea.get("tags", []),
            notes=idea.get("notes"),
            created_at=idea["created_at"],
            updated_at=idea["updated_at"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving idea: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve idea")


@router.patch("/api/ideas/{idea_id}", response_model=IdeaDetailResponse)
async def update_idea(
    idea_id: str,
    req: UpdateIdeaRequest,
    user: dict = Depends(get_current_user),
):
    """Update specific sections of an idea."""

    logger.info(f"User {user['id']} updating idea {idea_id}")

    supabase = get_supabase()

    try:
        # Build update dict (skip None values)
        update_data = {
            k: v for k, v in req.model_dump().items()
            if v is not None
        }

        # Always update timestamp
        update_data["updated_at"] = datetime.now().isoformat()

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        # Update in database
        response = supabase.table("ideas")\
            .update(update_data)\
            .eq("id", idea_id)\
            .eq("user_id", user["id"])\
            .execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Idea not found")

        idea = response.data[0]

        logger.info(f"Idea {idea_id} updated successfully")

        return IdeaDetailResponse(
            id=idea["id"],
            title=idea["title"],
            description=idea["description"],
            status=idea["status"],
            decomposition=idea.get("decomposition"),
            discover=idea.get("discover"),
            analyze=idea.get("analyze"),
            setup=idea.get("setup"),
            validation=idea.get("validate"),
            swot=idea.get("swot"),
            risks=idea.get("risks"),
            financials=idea.get("financials"),
            pricing=idea.get("pricing"),
            acquisition=idea.get("acquisition"),
            tags=idea.get("tags", []),
            notes=idea.get("notes"),
            created_at=idea["created_at"],
            updated_at=idea["updated_at"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating idea: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update idea")


@router.delete("/api/ideas/{idea_id}")
async def delete_idea(
    idea_id: str,
    user: dict = Depends(get_current_user),
):
    """Delete an idea."""

    logger.info(f"User {user['id']} deleting idea {idea_id}")

    supabase = get_supabase()

    try:
        # Delete from database
        response = supabase.table("ideas")\
            .delete()\
            .eq("id", idea_id)\
            .eq("user_id", user["id"])\
            .execute()

        logger.info(f"Idea {idea_id} deleted successfully")

        return {
            "status": "deleted",
            "id": idea_id,
            "message": "Idea deleted successfully"
        }

    except Exception as e:
        logger.error(f"Error deleting idea: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete idea")
