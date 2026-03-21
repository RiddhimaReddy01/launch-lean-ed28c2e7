"""
Progress tracking endpoints
GET /api/ideas/{id}/progress - View module completion status
PATCH /api/ideas/{id}/progress - Update module progress
GET /api/ideas/{id}/analyses - View all cached analyses
DELETE /api/ideas/{id}/analyses/{type} - Clear specific analysis cache
"""

import logging
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from supabase import create_client

from app.core.config import settings
from app.core.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


def get_supabase():
    """Get Supabase client."""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)


# ═══════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════

class ModuleProgress(BaseModel):
    module: str  # decompose, discover, analyze, setup, validate
    status: str  # pending, in_progress, completed
    completed_at: Optional[str] = None


class ProgressUpdate(BaseModel):
    module: str
    status: str  # pending, in_progress, completed


class ProgressResponse(BaseModel):
    idea_id: str
    title: str
    overall_progress: dict  # % complete
    modules: dict  # status of each module
    analyses: dict  # which analyses are cached


class AnalysisCache(BaseModel):
    type: str  # risks, pricing, financials, acquisition
    calculated_at: str
    assumptions: dict
    result_summary: str  # brief summary


# ═══════════════════════════════════════════════════════════════
# PROGRESS TRACKING
# ═══════════════════════════════════════════════════════════════

@router.get("/api/ideas/{idea_id}/progress", response_model=ProgressResponse)
async def get_progress(
    idea_id: str,
    user: dict = Depends(get_current_user),
):
    """Get module completion progress for an idea (like the plan phases)."""

    logger.info(f"User {user['id']} checking progress for idea {idea_id}")

    supabase = get_supabase()

    try:
        response = supabase.table("ideas")\
            .select(
                "id, title, decompose_status, decompose_completed_at, "
                "discover_status, discover_completed_at, "
                "analyze_status, analyze_completed_at, "
                "setup_status, setup_completed_at, "
                "validate_status, validate_completed_at, "
                "risks_calculated_at, pricing_calculated_at, "
                "financials_calculated_at, acquisition_calculated_at"
            )\
            .eq("id", idea_id)\
            .eq("user_id", user["id"])\
            .single()\
            .execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Idea not found")

        data = response.data

        # Calculate overall progress
        modules = {
            "decompose": {
                "status": data.get("decompose_status", "pending"),
                "completed_at": data.get("decompose_completed_at"),
            },
            "discover": {
                "status": data.get("discover_status", "pending"),
                "completed_at": data.get("discover_completed_at"),
            },
            "analyze": {
                "status": data.get("analyze_status", "pending"),
                "completed_at": data.get("analyze_completed_at"),
            },
            "setup": {
                "status": data.get("setup_status", "pending"),
                "completed_at": data.get("setup_completed_at"),
            },
            "validate": {
                "status": data.get("validate_status", "pending"),
                "completed_at": data.get("validate_completed_at"),
            },
        }

        completed = sum(1 for m in modules.values() if m["status"] == "completed")
        total = len(modules)

        analyses = {}
        for analysis_type in ["risks", "pricing", "financials", "acquisition"]:
            calc_key = f"{analysis_type}_calculated_at"
            if data.get(calc_key):
                analyses[analysis_type] = {
                    "cached": True,
                    "calculated_at": data.get(calc_key),
                }
            else:
                analyses[analysis_type] = {"cached": False}

        return ProgressResponse(
            idea_id=idea_id,
            title=data.get("title", "Untitled"),
            overall_progress={
                "completed": completed,
                "total": total,
                "percentage": int((completed / total) * 100) if total > 0 else 0,
            },
            modules=modules,
            analyses=analyses,
        )

    except Exception as e:
        logger.error(f"Error getting progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/api/ideas/{idea_id}/progress")
async def update_progress(
    idea_id: str,
    update: ProgressUpdate,
    user: dict = Depends(get_current_user),
):
    """Update module progress status."""

    logger.info(f"User {user['id']} updating progress for idea {idea_id}: {update.module} → {update.status}")

    supabase = get_supabase()

    # Validate module
    valid_modules = ["decompose", "discover", "analyze", "setup", "validate"]
    if update.module not in valid_modules:
        raise HTTPException(status_code=400, detail=f"Invalid module: {update.module}")

    valid_statuses = ["pending", "in_progress", "completed"]
    if update.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status: {update.status}")

    try:
        # Build update dict with status and optional timestamp
        update_data = {f"{update.module}_status": update.status}

        if update.status == "completed":
            update_data[f"{update.module}_completed_at"] = datetime.utcnow().isoformat()

        response = supabase.table("ideas")\
            .update(update_data)\
            .eq("id", idea_id)\
            .eq("user_id", user["id"])\
            .execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Idea not found")

        logger.info(f"Progress updated for {update.module}: {update.status}")

        return {
            "idea_id": idea_id,
            "module": update.module,
            "status": update.status,
            "completed_at": update_data.get(f"{update.module}_completed_at"),
        }

    except Exception as e:
        logger.error(f"Error updating progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════
# ANALYSIS CACHING
# ═══════════════════════════════════════════════════════════════

@router.get("/api/ideas/{idea_id}/analyses")
async def get_cached_analyses(
    idea_id: str,
    user: dict = Depends(get_current_user),
):
    """Get all cached analysis results for an idea."""

    logger.info(f"User {user['id']} retrieving cached analyses for idea {idea_id}")

    supabase = get_supabase()

    try:
        response = supabase.table("ideas")\
            .select(
                "id, title, "
                "risks, risks_calculated_at, risks_assumptions, "
                "pricing, pricing_calculated_at, pricing_assumptions, "
                "financials, financials_calculated_at, financials_assumptions, "
                "acquisition, acquisition_calculated_at, acquisition_assumptions"
            )\
            .eq("id", idea_id)\
            .eq("user_id", user["id"])\
            .single()\
            .execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Idea not found")

        data = response.data

        analyses = {
            "risks": {
                "cached": bool(data.get("risks")),
                "calculated_at": data.get("risks_calculated_at"),
                "assumptions": data.get("risks_assumptions"),
                "result": data.get("risks"),
            },
            "pricing": {
                "cached": bool(data.get("pricing")),
                "calculated_at": data.get("pricing_calculated_at"),
                "assumptions": data.get("pricing_assumptions"),
                "result": data.get("pricing"),
            },
            "financials": {
                "cached": bool(data.get("financials")),
                "calculated_at": data.get("financials_calculated_at"),
                "assumptions": data.get("financials_assumptions"),
                "result": data.get("financials"),
            },
            "acquisition": {
                "cached": bool(data.get("acquisition")),
                "calculated_at": data.get("acquisition_calculated_at"),
                "assumptions": data.get("acquisition_assumptions"),
                "result": data.get("acquisition"),
            },
        }

        return {
            "idea_id": idea_id,
            "title": data.get("title"),
            "analyses": analyses,
        }

    except Exception as e:
        logger.error(f"Error retrieving analyses: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/ideas/{idea_id}/analyses/{analysis_type}")
async def clear_analysis_cache(
    idea_id: str,
    analysis_type: str,
    user: dict = Depends(get_current_user),
):
    """Clear cached analysis result (forces recalculation on next request)."""

    logger.info(f"User {user['id']} clearing {analysis_type} cache for idea {idea_id}")

    valid_types = ["risks", "pricing", "financials", "acquisition"]
    if analysis_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid analysis type: {analysis_type}")

    supabase = get_supabase()

    try:
        update_data = {
            analysis_type: None,
            f"{analysis_type}_calculated_at": None,
            f"{analysis_type}_assumptions": None,
        }

        response = supabase.table("ideas")\
            .update(update_data)\
            .eq("id", idea_id)\
            .eq("user_id", user["id"])\
            .execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Idea not found")

        logger.info(f"Cache cleared for {analysis_type}")

        return {
            "idea_id": idea_id,
            "analysis_type": analysis_type,
            "cleared": True,
            "message": f"{analysis_type} cache cleared. Will recalculate on next request.",
        }

    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))
