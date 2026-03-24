"""
Validation Scorecard API
GET /api/ideas/{idea_id}/scorecard - Get validation scorecard verdict
"""

import logging
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


class ScorecardMetric(BaseModel):
    """Single scorecard metric."""
    metric: str
    target: float | int
    actual: float | int
    pct_met: float
    status: str  # on_track | behind | ahead


class ScorecardVerdict(BaseModel):
    """Overall verdict."""
    verdict: str  # GO | PIVOT | RECONSIDER | IN_PROGRESS
    pct_met: float
    reasoning: str
    metrics: list[ScorecardMetric]


# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════


def get_supabase():
    """Get Supabase client."""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)


def _calculate_verdict(pct_met: float) -> tuple[str, str]:
    """Determine verdict based on % of targets met.

    GO: ≥80% of targets met - Ready to scale
    PIVOT: 50-79% met - Some validation, but need to adjust
    RECONSIDER: 25-49% met - Limited validation, major changes needed
    IN_PROGRESS: <25% met - Too early to determine
    """
    if pct_met >= 80:
        return "GO", f"{pct_met:.0f}% of targets met. Ready to scale and invest more aggressively."
    elif pct_met >= 50:
        return "PIVOT", f"{pct_met:.0f}% of targets met. Some validation, but consider pivoting approach."
    elif pct_met >= 25:
        return "RECONSIDER", f"{pct_met:.0f}% of targets met. Limited validation. Major changes needed."
    else:
        return "IN_PROGRESS", f"{pct_met:.0f}% of targets met. Too early to determine direction."


# ═══════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════


@router.get("/api/ideas/{idea_id}/scorecard", response_model=ScorecardVerdict)
async def get_scorecard(
    idea_id: str,
    user: dict = Depends(get_current_user),
):
    """Get validation scorecard verdict for an idea."""
    logger.info(f"User {user['id']} fetching scorecard for idea {idea_id}")

    supabase = get_supabase()

    try:
        # Fetch idea to get scorecard targets
        idea_response = supabase.table("ideas").select("validate").eq("id", idea_id).eq("user_id", user["id"]).execute()

        if not idea_response.data:
            raise HTTPException(status_code=404, detail="Idea not found")

        idea_dict = idea_response.data[0] if isinstance(idea_response.data[0], dict) else dict(idea_response.data[0])
        validate_data = idea_dict.get("validate", {})

        if not validate_data:
            raise HTTPException(status_code=400, detail="No validation data found for this idea")

        # Get scorecard targets from validation response
        scorecard_targets = validate_data.get("scorecard", {})

        # Fetch latest validation experiments for actuals
        experiments_response = supabase.table("validation_experiments").select(
            "waitlist_signups,survey_completions,would_switch_rate,price_tolerance_avg,"
            "paid_signups,revenue_collected,ad_spend"
        ).eq("idea_id", idea_id).order("created_at", desc=True).limit(1).execute()

        actuals = {}
        if experiments_response.data:
            exp = experiments_response.data[0] if isinstance(experiments_response.data[0], dict) else dict(experiments_response.data[0])
            actuals = {
                "waitlist_signups": exp.get("waitlist_signups", 0),
                "survey_completions": exp.get("survey_completions", 0),
                "would_switch_rate": exp.get("would_switch_rate", 0),
                "price_tolerance_avg": exp.get("price_tolerance_avg", 0),
                "paid_signups": exp.get("paid_signups", 0),
                "revenue_collected": exp.get("revenue_collected", 0),
                "ad_spend": exp.get("ad_spend", 0),
            }

        # Calculate metrics
        metrics = []

        # Waitlist signups
        waitlist_target = scorecard_targets.get("waitlist_target", 50)
        waitlist_actual = actuals.get("waitlist_signups", 0)
        waitlist_pct = min(100, (waitlist_actual / waitlist_target * 100)) if waitlist_target > 0 else 0
        metrics.append(ScorecardMetric(
            metric="Waitlist Signups",
            target=waitlist_target,
            actual=waitlist_actual,
            pct_met=round(waitlist_pct, 1),
            status="on_track" if waitlist_pct >= 80 else "behind" if waitlist_pct >= 50 else "behind"
        ))

        # Survey completions
        survey_target = scorecard_targets.get("survey_target", 10)
        survey_actual = actuals.get("survey_completions", 0)
        survey_pct = min(100, (survey_actual / survey_target * 100)) if survey_target > 0 else 0
        metrics.append(ScorecardMetric(
            metric="Survey Completions",
            target=survey_target,
            actual=survey_actual,
            pct_met=round(survey_pct, 1),
            status="on_track" if survey_pct >= 80 else "behind"
        ))

        # Would switch %
        switch_target = scorecard_targets.get("switch_pct_target", 60)
        switch_actual = actuals.get("would_switch_rate", 0) * 100  # Convert from decimal to percentage
        switch_pct = min(100, (switch_actual / switch_target * 100)) if switch_target > 0 else 0
        metrics.append(ScorecardMetric(
            metric="Would Switch (%)",
            target=switch_target,
            actual=round(switch_actual, 1),
            pct_met=round(switch_pct, 1),
            status="on_track" if switch_pct >= 80 else "behind"
        ))

        # Price tolerance
        price_target = scorecard_targets.get("price_tolerance_target", 12.0)
        price_actual = actuals.get("price_tolerance_avg", 0)
        price_pct = min(100, (price_actual / price_target * 100)) if price_target > 0 else 0
        metrics.append(ScorecardMetric(
            metric="Price Tolerance ($)",
            target=price_target,
            actual=round(price_actual, 2),
            pct_met=round(price_pct, 1),
            status="on_track" if price_pct >= 80 else "behind"
        ))

        # Paid signups
        paid_target = scorecard_targets.get("paid_signups_target", 5)
        paid_actual = actuals.get("paid_signups", 0)
        paid_pct = min(100, (paid_actual / paid_target * 100)) if paid_target > 0 else 0
        metrics.append(ScorecardMetric(
            metric="Paid Signups",
            target=paid_target,
            actual=paid_actual,
            pct_met=round(paid_pct, 1),
            status="on_track" if paid_pct >= 80 else "behind"
        ))

        # LTV/CAC ratio (revenue / ad_spend / paid_signups)
        revenue = actuals.get("revenue_collected", 0)
        ad_spend = actuals.get("ad_spend", 0)
        cac = (ad_spend / paid_actual) if paid_actual > 0 else 0
        ltv = (revenue / paid_actual) if paid_actual > 0 else 0
        ltv_cac_actual = (ltv / cac) if cac > 0 else 0
        ltv_cac_target = scorecard_targets.get("ltv_cac_ratio_target", 3.0)
        ltv_cac_pct = min(100, (ltv_cac_actual / ltv_cac_target * 100)) if ltv_cac_target > 0 else 0
        metrics.append(ScorecardMetric(
            metric="LTV/CAC Ratio",
            target=ltv_cac_target,
            actual=round(ltv_cac_actual, 2),
            pct_met=round(ltv_cac_pct, 1),
            status="on_track" if ltv_cac_pct >= 80 else "behind"
        ))

        # Calculate overall % met (simple average)
        overall_pct = round(sum(m.pct_met for m in metrics) / len(metrics), 1) if metrics else 0

        # Determine verdict
        verdict, reasoning = _calculate_verdict(overall_pct)

        return ScorecardVerdict(
            verdict=verdict,
            pct_met=overall_pct,
            reasoning=reasoning,
            metrics=metrics,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get scorecard: {e}")
        raise HTTPException(status_code=500, detail="Failed to get scorecard")
