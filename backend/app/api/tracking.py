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


def _calculate_cac_ltv(
    paid_signups: int,
    revenue_collected: float,
    ad_spend: float,
    price_tolerance: float,
    months_expected: int = 12,
) -> tuple[float | None, float | None]:
    """Calculate CAC and LTV/CAC ratio."""
    # CAC = Cost per acquisition
    cac = None
    if paid_signups > 0 and ad_spend > 0:
        cac = ad_spend / paid_signups

    # LTV/CAC = How many times CAC is revenue
    ltv_cac_ratio = None
    if paid_signups > 0:
        avg_customer_value = revenue_collected / paid_signups if paid_signups > 0 else 0
        estimated_ltv = avg_customer_value * months_expected
        if cac and cac > 0:
            ltv_cac_ratio = estimated_ltv / cac

    return cac, ltv_cac_ratio


def _calculate_verdict(
    signups: int,
    switch_rate: float,
    price_tolerance: float,
    paid_signups: int = 0,
    revenue_collected: float = 0.0,
    cac: float | None = None,
    ltv_cac_ratio: float | None = None,
) -> tuple[str, str]:
    """Calculate GO/PIVOT/KILL verdict with revenue validation."""
    has_data = signups > 0 or switch_rate > 0 or price_tolerance > 0

    if not has_data:
        return "awaiting", "Enter your experiment results to get a recommendation."

    # Revenue validation: check if people actually paid
    if paid_signups == 0 and signups > 0:
        return "pivot", f"High interest ({signups} signups) but zero conversions to paid. Adjust pricing, positioning, or value prop."

    # Strong signal: good signups + intent + price + revenue
    if signups >= 50 and switch_rate >= 60 and price_tolerance >= 8 and paid_signups > 0:
        ltv_text = f"LTV/CAC ratio: {ltv_cac_ratio:.1f}x" if ltv_cac_ratio else ""
        return "go", f"Strong demand signal. {signups} signups, {paid_signups} paid. {ltv_text} Move forward."

    # Weak signal: low engagement across board
    if signups < 30 and switch_rate < 30:
        return "kill", "Low interest across channels. Consider a fundamentally different value proposition."

    # Moderate signal: some traction
    if signups >= 30 and switch_rate >= 40 and paid_signups > 0:
        conversion = (paid_signups / signups * 100) if signups > 0 else 0
        return "pivot", f"Moderate interest ({signups} signups, {conversion:.0f}% paid conversion). Refine positioning or pricing."

    # Price issue
    if price_tolerance < 6 and signups > 50:
        return "pivot", "Strong interest but low price tolerance. Consider repositioning, bundling, or freemium model."

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

    # Calculate CAC and LTV/CAC ratio (NEW)
    cac, ltv_cac_ratio = _calculate_cac_ltv(
        req.metrics.paid_signups,
        req.metrics.revenue_collected,
        req.metrics.ad_spend,
        req.metrics.price_tolerance_avg,
    )

    # Calculate verdict (now includes revenue validation)
    verdict, reasoning = _calculate_verdict(
        req.metrics.waitlist_signups,
        req.metrics.would_switch_rate,
        req.metrics.price_tolerance_avg,
        req.metrics.paid_signups,
        req.metrics.revenue_collected,
        cac,
        ltv_cac_ratio,
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
                # NEW: Revenue metrics
                "paid_signups": req.metrics.paid_signups,
                "revenue_collected": req.metrics.revenue_collected,
                "ad_spend": req.metrics.ad_spend,
                "cac": cac,
                "ltv_cac_ratio": ltv_cac_ratio,
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
            # NEW: Revenue metrics
            paid_signups=experiment.get("paid_signups", 0),
            revenue_collected=experiment.get("revenue_collected", 0.0),
            ad_spend=experiment.get("ad_spend", 0.0),
            cac=experiment.get("cac"),
            ltv_cac_ratio=experiment.get("ltv_cac_ratio"),
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
                    # NEW: Revenue metrics
                    paid_signups=exp.get("paid_signups", 0),
                    revenue_collected=exp.get("revenue_collected", 0.0),
                    ad_spend=exp.get("ad_spend", 0.0),
                    cac=exp.get("cac"),
                    ltv_cac_ratio=exp.get("ltv_cac_ratio"),
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
        # NEW: Revenue metrics
        if req.paid_signups is not None:
            update_data["paid_signups"] = req.paid_signups
        if req.revenue_collected is not None:
            update_data["revenue_collected"] = req.revenue_collected
        if req.ad_spend is not None:
            update_data["ad_spend"] = req.ad_spend

        # Recalculate verdict and CAC/LTV if metrics changed
        experiment = fetch_response.data[0]
        signups = update_data.get("waitlist_signups", experiment["waitlist_signups"])
        switch_rate = update_data.get("would_switch_rate", experiment["would_switch_rate"])
        price = update_data.get("price_tolerance_avg", experiment["price_tolerance_avg"])
        paid_signups = update_data.get("paid_signups", experiment.get("paid_signups", 0))
        revenue = update_data.get("revenue_collected", experiment.get("revenue_collected", 0.0))
        ad_spend = update_data.get("ad_spend", experiment.get("ad_spend", 0.0))

        # Recalculate CAC/LTV
        cac, ltv_cac_ratio = _calculate_cac_ltv(paid_signups, revenue, ad_spend, price)
        if cac is not None:
            update_data["cac"] = cac
        if ltv_cac_ratio is not None:
            update_data["ltv_cac_ratio"] = ltv_cac_ratio

        verdict, reasoning = _calculate_verdict(signups, switch_rate, price, paid_signups, revenue, cac, ltv_cac_ratio)
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
            # NEW: Revenue metrics
            paid_signups=updated.get("paid_signups", 0),
            revenue_collected=updated.get("revenue_collected", 0.0),
            ad_spend=updated.get("ad_spend", 0.0),
            cac=updated.get("cac"),
            ltv_cac_ratio=updated.get("ltv_cac_ratio"),
            verdict=updated["verdict"],
            reasoning=updated["reasoning"],
            created_at=updated["created_at"],
            updated_at=updated["updated_at"],
        )

    except Exception as e:
        logger.error(f"Failed to update validation experiment: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update experiment")
