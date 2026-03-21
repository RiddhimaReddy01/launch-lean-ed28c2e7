"""
Validation Experiment Tracking
POST /api/validation-experiments - Save validation experiment
GET /api/validation-experiments/{idea_id} - Fetch all experiments for an idea
PATCH /api/validation-experiments/{id} - Update experiment metrics
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from app.core.auth import require_user
from app.core.config import get_settings
from app.schemas.models import (
    CreateValidationExperimentRequest,
    UpdateValidationExperimentRequest,
    ValidationExperimentResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()

# Initialize Supabase client (optional if credentials not configured)
from supabase import create_client

supabase = None
try:
    if settings.SUPABASE_URL and not settings.SUPABASE_URL.startswith("your_"):
        supabase = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_ANON_KEY,
        )
        logger.info("Supabase client initialized")
except Exception as e:
    logger.warning(f"Could not initialize Supabase: {e}")


def _calculate_verdict(
    signups: int,
    switch_rate: float,
    price_tolerance: float,
) -> tuple[str, str]:
    """Calculate GO/PIVOT/KILL verdict and reasoning."""
    has_data = signups > 0 or switch_rate > 0 or price_tolerance > 0

    if not has_data:
        return "awaiting", "Enter your experiment results to get a recommendation."

    if signups >= 150 and switch_rate >= 60 and price_tolerance >= 8:
        return "go", "Strong demand signal with healthy price tolerance. Move forward with confidence."

    if signups < 30 and switch_rate < 30:
        return "kill", "Low interest across channels. Consider a fundamentally different value proposition."

    if signups >= 80 and switch_rate >= 40:
        return "pivot", "Moderate interest — refine positioning, adjust pricing, or narrow the segment."

    if price_tolerance < 6 and signups > 50:
        return "pivot", "Strong interest but low price tolerance — consider repositioning pricing."

    return "pivot", "Mixed signals. Some interest exists but key metrics need improvement."


@router.post("/api/validation-experiments", response_model=ValidationExperimentResponse)
async def create_validation_experiment(
    req: CreateValidationExperimentRequest,
    user: dict = Depends(require_user),
):
    """Save a new validation experiment."""
    if not supabase:
        raise HTTPException(
            status_code=503,
            detail="Database not configured. Please configure Supabase credentials."
        )

    user_id = user.get("id")

    # Calculate verdict
    verdict, reasoning = _calculate_verdict(
        req.metrics.waitlist_signups,
        req.metrics.would_switch_rate,
        req.metrics.price_tolerance_avg,
    )

    try:
        # Insert into Supabase
        response = supabase.table("validation_experiments").insert(
            {
                "user_id": user_id,
                "idea_id": req.idea_id,
                "methods": req.methods,
                "waitlist_signups": req.metrics.waitlist_signups,
                "survey_completions": req.metrics.survey_completions,
                "would_switch_rate": req.metrics.would_switch_rate,
                "price_tolerance_avg": req.metrics.price_tolerance_avg,
                "community_engagement": req.metrics.community_engagement,
                "reddit_upvotes": req.metrics.reddit_upvotes,
                "verdict": verdict,
                "reasoning": reasoning,
            }
        ).execute()

        if not response.data:
            raise HTTPException(status_code=400, detail="Failed to create experiment")

        experiment = response.data[0]
        return ValidationExperimentResponse(
            id=experiment["id"],
            idea_id=experiment["idea_id"],
            methods=experiment["methods"] or [],
            waitlist_signups=experiment["waitlist_signups"],
            survey_completions=experiment["survey_completions"],
            would_switch_rate=experiment["would_switch_rate"],
            price_tolerance_avg=experiment["price_tolerance_avg"],
            community_engagement=experiment["community_engagement"],
            reddit_upvotes=experiment["reddit_upvotes"],
            verdict=experiment["verdict"],
            reasoning=experiment["reasoning"],
            created_at=experiment["created_at"],
            updated_at=experiment["updated_at"],
        )

    except Exception as e:
        logger.error(f"Failed to create validation experiment: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create experiment")


@router.get("/api/validation-experiments/{idea_id}")
async def get_validation_experiments(
    idea_id: str,
    user: dict = Depends(require_user),
):
    """Fetch all validation experiments for an idea."""
    user_id = user.get("id")

    try:
        response = supabase.table("validation_experiments").select("*").eq(
            "idea_id", idea_id
        ).eq("user_id", user_id).order("created_at", desc=True).execute()

        experiments = []
        for exp in response.data:
            experiments.append(
                ValidationExperimentResponse(
                    id=exp["id"],
                    idea_id=exp["idea_id"],
                    methods=exp["methods"] or [],
                    waitlist_signups=exp["waitlist_signups"],
                    survey_completions=exp["survey_completions"],
                    would_switch_rate=exp["would_switch_rate"],
                    price_tolerance_avg=exp["price_tolerance_avg"],
                    community_engagement=exp["community_engagement"],
                    reddit_upvotes=exp["reddit_upvotes"],
                    verdict=exp["verdict"],
                    reasoning=exp["reasoning"],
                    created_at=exp["created_at"],
                    updated_at=exp["updated_at"],
                )
            )

        return {"experiments": experiments, "count": len(experiments)}

    except Exception as e:
        logger.error(f"Failed to fetch validation experiments: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch experiments")


@router.patch("/api/validation-experiments/{experiment_id}", response_model=ValidationExperimentResponse)
async def update_validation_experiment(
    experiment_id: str,
    req: UpdateValidationExperimentRequest,
    user: dict = Depends(require_user),
):
    """Update validation experiment metrics."""
    user_id = user.get("id")

    try:
        # First fetch the experiment to verify ownership
        fetch_response = supabase.table("validation_experiments").select("*").eq(
            "id", experiment_id
        ).eq("user_id", user_id).execute()

        if not fetch_response.data:
            raise HTTPException(status_code=404, detail="Experiment not found")

        # Build update dict with only provided fields
        update_data = {}
        if req.waitlist_signups is not None:
            update_data["waitlist_signups"] = req.waitlist_signups
        if req.survey_completions is not None:
            update_data["survey_completions"] = req.survey_completions
        if req.would_switch_rate is not None:
            update_data["would_switch_rate"] = req.would_switch_rate
        if req.price_tolerance_avg is not None:
            update_data["price_tolerance_avg"] = req.price_tolerance_avg
        if req.community_engagement is not None:
            update_data["community_engagement"] = req.community_engagement
        if req.reddit_upvotes is not None:
            update_data["reddit_upvotes"] = req.reddit_upvotes

        # Recalculate verdict if metrics changed
        experiment = fetch_response.data[0]
        signups = update_data.get("waitlist_signups", experiment["waitlist_signups"])
        switch_rate = update_data.get("would_switch_rate", experiment["would_switch_rate"])
        price = update_data.get("price_tolerance_avg", experiment["price_tolerance_avg"])

        verdict, reasoning = _calculate_verdict(signups, switch_rate, price)
        update_data["verdict"] = verdict
        update_data["reasoning"] = reasoning

        # Update in Supabase
        response = supabase.table("validation_experiments").update(update_data).eq(
            "id", experiment_id
        ).execute()

        if not response.data:
            raise HTTPException(status_code=400, detail="Failed to update experiment")

        updated = response.data[0]
        return ValidationExperimentResponse(
            id=updated["id"],
            idea_id=updated["idea_id"],
            methods=updated["methods"] or [],
            waitlist_signups=updated["waitlist_signups"],
            survey_completions=updated["survey_completions"],
            would_switch_rate=updated["would_switch_rate"],
            price_tolerance_avg=updated["price_tolerance_avg"],
            community_engagement=updated["community_engagement"],
            reddit_upvotes=updated["reddit_upvotes"],
            verdict=updated["verdict"],
            reasoning=updated["reasoning"],
            created_at=updated["created_at"],
            updated_at=updated["updated_at"],
        )

    except Exception as e:
        logger.error(f"Failed to update validation experiment: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update experiment")
