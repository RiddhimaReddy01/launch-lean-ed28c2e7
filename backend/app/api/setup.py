"""
POST /api/setup - Generate launch plan (Cost Tiers, Suppliers, Team, Timeline)
"""

import logging
from fastapi import APIRouter, Depends
from app.core.auth import optional_user
from app.schemas.models import SetupRequest, SetupResponse
from app.services.setup_service import generate_full_setup

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/api/setup", response_model=SetupResponse)
async def setup_section(
    req: SetupRequest,
    user: dict | None = Depends(optional_user),
):
    """Generate complete launch plan from ANALYZE data."""

    decomp = req.decomposition.model_dump() if hasattr(req.decomposition, 'model_dump') else req.decomposition

    # Extract prior analysis data
    prior_context = req.prior_context or {}
    costs = prior_context.get("costs", {})
    root_causes = prior_context.get("root_causes", {}).get("root_causes", [])
    customers = prior_context.get("customers", {})

    # User selects tier (LEAN | MID | PREMIUM)
    selected_tier = req.selected_tier if hasattr(req, 'selected_tier') else "MID"

    logger.info(f"[SETUP] Generating setup for tier={selected_tier}")

    try:
        # Generate all 4 components with caching
        setup_data = await generate_full_setup(
            decomposition=decomp,
            costs=costs,
            root_causes=root_causes,
            customers=customers,
            selected_tier=selected_tier
        )

        response = SetupResponse(
            cost_tiers=setup_data["cost_tiers"],
            suppliers=setup_data["suppliers"],
            team=setup_data["team"],
            timeline=setup_data["timeline"]
        )

        logger.info(f"[SETUP] Success: {len(response.cost_tiers)} tiers, {len(response.suppliers)} suppliers, "
                    f"{len(response.team)} roles, {len(response.timeline)} phases")

        return response

    except Exception as e:
        logger.error(f"[SETUP] Failed: {e}")
        # Return empty response rather than error
        return SetupResponse(
            cost_tiers=[],
            suppliers=[],
            team=[],
            timeline=[]
        )
