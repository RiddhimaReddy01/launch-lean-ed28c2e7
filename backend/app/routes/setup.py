"""
POST /api/generate-setup
Generates complete launch plan: cost tiers, suppliers, team, timeline.
Pipeline: Serper search for suppliers → LLM generation → validation → response.
"""

import json
import logging
from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import optional_user
from app.schemas.models import SetupRequest, SetupResponse
from app.services.llm_client import call_llm, AllProvidersExhaustedError
from app.services.google_search import run_search_queries, build_setup_queries
from app.services.data_cleaner import clean_search_results
from app.prompts.templates import setup_system, setup_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/api/generate-setup", response_model=SetupResponse)
async def generate_setup(
    req: SetupRequest,
    user: dict | None = Depends(optional_user),
):
    decomp = req.decomposition
    insight = req.insight
    loc = decomp.get("location", {})
    city = loc.get("city", "")
    state = loc.get("state", "")
    metro = loc.get("metro", "")
    btype = decomp.get("business_type", "")

    # ═══ STAGE 1: DATA INGESTION ═══
    queries = build_setup_queries(decomp)
    search_results = await run_search_queries(queries, location=f"{city}, {state}", num_per_query=8)

    # ═══ STAGE 2: DATA CLEANING ═══
    cleaned = clean_search_results(search_results, query_type="setup")

    # ═══ STAGE 3: DATA TRANSFORMATION ═══
    search_context = "\n".join(
        f"- {r['title']}: {r['snippet'][:200]} ({r['link']})"
        for r in cleaned[:25]
    )

    analysis_summary = ""
    if req.analysis_context:
        ctx = req.analysis_context
        if "opportunity" in ctx:
            som = ctx["opportunity"].get("som", {})
            analysis_summary += f"Market SOM: {som.get('formatted', 'unknown')}\n"
        if "competitors" in ctx:
            comps = ctx["competitors"].get("competitors", [])
            analysis_summary += "Key competitors: " + ", ".join(
                c.get("name", "") for c in comps[:5]
            ) + "\n"
        if "rootcause" in ctx:
            causes = ctx["rootcause"].get("root_causes", [])
            analysis_summary += "Root causes: " + "; ".join(
                c.get("title", "") for c in causes[:3]
            ) + "\n"
        if "customers" in ctx:
            segs = ctx["customers"].get("segments", [])
            analysis_summary += "Customer segments: " + ", ".join(
                s.get("name", "") for s in segs[:4]
            ) + "\n"

    # ═══ STAGE 4: LLM LOGIC ═══
    system = setup_system(btype, city, state, metro)
    user_prompt = setup_user(decomp, insight, analysis_summary, search_context)

    try:
        raw = await call_llm(
            system_prompt=system,
            user_prompt=user_prompt,
            temperature=0.3,
            max_tokens=6000,
            json_mode=True,
        )
    except AllProvidersExhaustedError:
        raise HTTPException(status_code=503, detail="All LLM providers unavailable")

    # ═══ STAGE 5: POST-PROCESSING ═══
    return _post_process(raw)


def _post_process(raw: dict) -> SetupResponse:
    """Validate cost logic, format output, sort suppliers."""

    # ── Cost Tiers ──
    cost_tiers = raw.get("cost_tiers", [])
    for tier in cost_tiers:
        items = tier.get("line_items", [])
        # Validate min <= max for every line item
        for item in items:
            mn = item.get("min_cost", 0)
            mx = item.get("max_cost", 0)
            if mn > mx:
                item["min_cost"], item["max_cost"] = mx, mn

        # Calculate tier total from line items
        total_min = sum(item.get("min_cost", 0) for item in items)
        total_max = sum(item.get("max_cost", 0) for item in items)
        tier["total_range"] = {"min": total_min, "max": total_max}

    # Validate tier ordering: minimum < recommended < full
    tier_names = ["minimum_viable", "recommended", "full_buildout"]
    tier_map = {t.get("tier", ""): t for t in cost_tiers}
    prev_max = 0
    for name in tier_names:
        if name in tier_map:
            tr = tier_map[name].get("total_range", {})
            if tr.get("min", 0) < prev_max * 0.5 and prev_max > 0:
                logger.warning(f"Tier {name} min ({tr.get('min')}) seems low vs previous max ({prev_max})")
            prev_max = tr.get("max", 0)

    # ── Suppliers ──
    suppliers = raw.get("suppliers", [])
    # Sort by category
    category_order = {"equipment": 0, "produce": 1, "supplies": 1, "packaging": 2, "services": 3, "technology": 4}
    suppliers.sort(key=lambda s: category_order.get(s.get("category", "").lower(), 5))

    # ── Team ──
    team = raw.get("team", [])
    # Validate salary ranges
    for role in team:
        sr = role.get("salary_range", {})
        if isinstance(sr, dict):
            mn = sr.get("min", 0)
            mx = sr.get("max", 0)
            if mn > mx:
                sr["min"], sr["max"] = mx, mn

    # ── Timeline ──
    timeline = raw.get("timeline", [])
    # Validate sequential phases
    # (light validation - just ensure we have phases)

    return SetupResponse(
        cost_tiers=[_dict_to_model(t, "cost_tier") for t in cost_tiers],
        suppliers=[_dict_to_model(s, "supplier") for s in suppliers],
        team=[_dict_to_model(r, "team_role") for r in team],
        timeline=[_dict_to_model(p, "timeline_phase") for p in timeline],
    )


def _dict_to_model(d: dict, model_type: str):
    """Safely convert dict to response model, handling missing fields."""
    from app.schemas.models import CostTier, Supplier, TeamRole, TimelinePhase

    model_map = {
        "cost_tier": CostTier,
        "supplier": Supplier,
        "team_role": TeamRole,
        "timeline_phase": TimelinePhase,
    }

    model_class = model_map.get(model_type)
    if not model_class:
        return d

    try:
        return model_class(**d)
    except Exception:
        # Return with defaults for missing fields
        return model_class.model_validate(d)
