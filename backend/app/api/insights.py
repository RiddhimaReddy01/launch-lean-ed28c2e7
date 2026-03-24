"""
Insights Persistence API
POST   /api/ideas/{idea_id}/insights - Save an insight
GET    /api/ideas/{idea_id}/insights - List insights for an idea
PATCH  /api/ideas/{idea_id}/insights/{insight_id} - Update insight
DELETE /api/ideas/{idea_id}/insights/{insight_id} - Delete insight
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
# SCHEMAS
# ═══════════════════════════════════════════════════════════════


class SaveInsightRequest(BaseModel):
    """Request to save an insight."""
    section: str = Field(..., description="Section: opportunity, customers, competitors, etc")
    title: str = Field(..., min_length=3, max_length=255)
    content: dict = Field(..., description="Full insight content (JSONB)")
    tags: Optional[list[str]] = None
    pinned: bool = False


class UpdateInsightRequest(BaseModel):
    """Request to update an insight."""
    title: Optional[str] = None
    content: Optional[dict] = None
    tags: Optional[list[str]] = None
    pinned: Optional[bool] = None


class InsightResponse(BaseModel):
    """Response model for insight."""
    id: str
    idea_id: str
    section: str
    title: str
    content: dict
    tags: list[str]
    pinned: bool
    created_at: str
    updated_at: str


# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════


def get_supabase():
    """Get Supabase client."""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)


async def _verify_idea_ownership(idea_id: str, user_id: str) -> bool:
    """Verify that user owns the idea."""
    supabase = get_supabase()
    try:
        response = supabase.table("ideas").select("id").eq("id", idea_id).eq("user_id", user_id).execute()
        return len(response.data) > 0
    except Exception:
        return False


# ═══════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════


@router.post("/api/ideas/{idea_id}/insights", response_model=InsightResponse)
async def save_insight(
    idea_id: str,
    req: SaveInsightRequest,
    user: dict = Depends(get_current_user),
):
    """Save an insight for an idea."""
    logger.info(f"User {user['id']} saving insight for idea {idea_id}: {req.title}")

    # Verify ownership
    owns_idea = await _verify_idea_ownership(idea_id, user["id"])
    if not owns_idea:
        raise HTTPException(status_code=403, detail="Not authorized to save insights for this idea")

    supabase = get_supabase()

    insight_data = {
        "user_id": user["id"],
        "idea_id": idea_id,
        "section": req.section,
        "title": req.title,
        "content": req.content,
        "tags": req.tags or [],
        "pinned": req.pinned,
    }

    try:
        response = supabase.table("idea_insights").insert(insight_data).execute()

        if not response.data:
            raise HTTPException(status_code=400, detail="Failed to save insight")

        raw_insight = response.data[0]
        insight_dict = raw_insight if isinstance(raw_insight, dict) else dict(raw_insight)

        logger.info(f"Insight saved with ID: {insight_dict.get('id')}")

        return InsightResponse(
            id=str(insight_dict.get("id", "")),
            idea_id=str(insight_dict.get("idea_id", "")),
            section=str(insight_dict.get("section", "")),
            title=str(insight_dict.get("title", "")),
            content=insight_dict.get("content", {}),
            tags=list(insight_dict.get("tags", [])),
            pinned=bool(insight_dict.get("pinned", False)),
            created_at=str(insight_dict.get("created_at", "")),
            updated_at=str(insight_dict.get("updated_at", "")),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save insight: {e}")
        raise HTTPException(status_code=500, detail="Failed to save insight")


@router.get("/api/ideas/{idea_id}/insights")
async def list_insights(
    idea_id: str,
    section: Optional[str] = None,
    user: dict = Depends(get_current_user),
):
    """List insights for an idea, optionally filtered by section."""
    logger.info(f"User {user['id']} fetching insights for idea {idea_id}")

    # Verify ownership
    owns_idea = await _verify_idea_ownership(idea_id, user["id"])
    if not owns_idea:
        raise HTTPException(status_code=403, detail="Not authorized to view insights for this idea")

    supabase = get_supabase()

    try:
        query = supabase.table("idea_insights").select("*").eq("idea_id", idea_id).eq("user_id", user["id"])

        if section:
            query = query.eq("section", section)

        response = query.order("pinned", desc=True).order("created_at", desc=True).execute()

        insights = []
        for raw in response.data:
            insight_dict = raw if isinstance(raw, dict) else dict(raw)
            insights.append(InsightResponse(
                id=str(insight_dict.get("id", "")),
                idea_id=str(insight_dict.get("idea_id", "")),
                section=str(insight_dict.get("section", "")),
                title=str(insight_dict.get("title", "")),
                content=insight_dict.get("content", {}),
                tags=list(insight_dict.get("tags", [])),
                pinned=bool(insight_dict.get("pinned", False)),
                created_at=str(insight_dict.get("created_at", "")),
                updated_at=str(insight_dict.get("updated_at", "")),
            ))

        return {"insights": insights}

    except Exception as e:
        logger.error(f"Failed to list insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to list insights")


@router.patch("/api/ideas/{idea_id}/insights/{insight_id}", response_model=InsightResponse)
async def update_insight(
    idea_id: str,
    insight_id: str,
    req: UpdateInsightRequest,
    user: dict = Depends(get_current_user),
):
    """Update an insight."""
    logger.info(f"User {user['id']} updating insight {insight_id}")

    # Verify ownership
    owns_idea = await _verify_idea_ownership(idea_id, user["id"])
    if not owns_idea:
        raise HTTPException(status_code=403, detail="Not authorized to update insights for this idea")

    supabase = get_supabase()

    try:
        # Check if insight exists and belongs to user
        check_response = supabase.table("idea_insights").select("id").eq("id", insight_id).eq("user_id", user["id"]).execute()
        if not check_response.data:
            raise HTTPException(status_code=404, detail="Insight not found")

        # Prepare update data (only update non-None fields)
        update_data = {}
        if req.title is not None:
            update_data["title"] = req.title
        if req.content is not None:
            update_data["content"] = req.content
        if req.tags is not None:
            update_data["tags"] = req.tags
        if req.pinned is not None:
            update_data["pinned"] = req.pinned

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        update_data["updated_at"] = datetime.utcnow().isoformat()

        response = supabase.table("idea_insights").update(update_data).eq("id", insight_id).execute()

        if not response.data:
            raise HTTPException(status_code=400, detail="Failed to update insight")

        raw_insight = response.data[0]
        insight_dict = raw_insight if isinstance(raw_insight, dict) else dict(raw_insight)

        return InsightResponse(
            id=str(insight_dict.get("id", "")),
            idea_id=str(insight_dict.get("idea_id", "")),
            section=str(insight_dict.get("section", "")),
            title=str(insight_dict.get("title", "")),
            content=insight_dict.get("content", {}),
            tags=list(insight_dict.get("tags", [])),
            pinned=bool(insight_dict.get("pinned", False)),
            created_at=str(insight_dict.get("created_at", "")),
            updated_at=str(insight_dict.get("updated_at", "")),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update insight: {e}")
        raise HTTPException(status_code=500, detail="Failed to update insight")


@router.delete("/api/ideas/{idea_id}/insights/{insight_id}")
async def delete_insight(
    idea_id: str,
    insight_id: str,
    user: dict = Depends(get_current_user),
):
    """Delete an insight."""
    logger.info(f"User {user['id']} deleting insight {insight_id}")

    # Verify ownership
    owns_idea = await _verify_idea_ownership(idea_id, user["id"])
    if not owns_idea:
        raise HTTPException(status_code=403, detail="Not authorized to delete insights for this idea")

    supabase = get_supabase()

    try:
        # Check if insight exists and belongs to user
        check_response = supabase.table("idea_insights").select("id").eq("id", insight_id).eq("user_id", user["id"]).execute()
        if not check_response.data:
            raise HTTPException(status_code=404, detail="Insight not found")

        # Delete
        supabase.table("idea_insights").delete().eq("id", insight_id).execute()

        logger.info(f"Insight {insight_id} deleted")

        return {"message": "Insight deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete insight: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete insight")
