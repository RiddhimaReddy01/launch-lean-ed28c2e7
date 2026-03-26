"""
POST /api/setup - Generate launch plan (Cost Tiers, Suppliers, Team, Timeline)
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
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
    """Generate complete launch plan from business idea."""
    # Reuse upstream context when available to avoid recomputing shared work.
    if req.decomposition:
        decomp = req.decomposition
    elif req.idea:
        from app.api.decompose import decompose_idea
        from app.schemas.models import DecomposeRequest

        decompose_req = DecomposeRequest(idea=req.idea)
        decomp_response = await decompose_idea(decompose_req, user=user)
        decomp = decomp_response.model_dump() if hasattr(decomp_response, 'model_dump') else decomp_response
    else:
        raise HTTPException(
            status_code=400,
            detail="Provide either 'idea' or 'decomposition'",
        )

    # Setup-specific generation uses prior analysis context, but does not need to rerun discover.
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
            timeline=setup_data["timeline"],
            recommendation=setup_data.get("recommendation"),
            revenue_projection=setup_data.get("revenue_projection"),
            founder_time_allocation=setup_data.get("founder_time_allocation", []),
            vendor_benchmarks=setup_data.get("vendor_benchmarks", []),
        )

        logger.info(f"[SETUP] Success: {len(response.cost_tiers)} tiers, {len(response.suppliers)} suppliers, "
                    f"{len(response.team)} roles, {len(response.timeline)} phases")

        return response

    except Exception as e:
        logger.error(f"[SETUP] Failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate setup plan: {str(e)}"
        )
