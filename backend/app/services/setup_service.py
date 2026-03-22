"""
SETUP tab service: Generate launch plan with Cost Tiers, Suppliers, Team, Timeline.
Handles LLM calls, caching, and deterministic calculations.
"""

import json
import logging
from app.services.llm_client import call_llm
from app.prompts.templates import (
    setup_suppliers_system, setup_suppliers_user,
    setup_team_system, setup_team_user,
    setup_timeline_system, setup_timeline_user
)

logger = logging.getLogger(__name__)

# Cost tier multipliers (deterministic, no LLM)
TIER_MULTIPLIERS = {
    "LEAN": {
        "min_multiplier": 0.6,
        "max_multiplier": 0.8,
        "philosophy": "Speed + founder effort, no external hires",
        "approach": "No-code tools, freelancers, DIY",
        "team_size": "1",
        "timeline_weeks": 16
    },
    "MID": {
        "min_multiplier": 1.0,
        "max_multiplier": 1.0,
        "philosophy": "Balanced speed, quality, team",
        "approach": "Custom app, 1 FTE engineer",
        "team_size": "1-2",
        "timeline_weeks": 24
    },
    "PREMIUM": {
        "min_multiplier": 1.2,
        "max_multiplier": 1.8,
        "philosophy": "Quality + team, higher burn",
        "approach": "Custom + team, multiple hires",
        "team_size": "2-3",
        "timeline_weeks": 32
    }
}


# ═══ CACHE OPERATIONS ═══

async def get_cached_setup(business_type: str, city: str, state: str, tier: str, component: str = None):
    """Get cached SETUP data. Cache currently disabled."""
    return None


async def cache_setup_data(business_type: str, city: str, state: str, tier: str, component: str, data: dict, ttl_days: int = 30):
    """Store SETUP component in cache. Cache currently disabled."""
    logger.debug(f"[SETUP] Cache storage skipped for {component}")


# ═══ COST TIERS (Deterministic - No LLM) ═══

def generate_cost_tiers(costs: dict) -> list[dict]:
    """Generate 3 cost tiers from COSTS data using multipliers."""

    if not costs or "total_range" not in costs:
        logger.warning("[SETUP] No costs data provided, using defaults")
        return []

    total_min = costs.get("total_range", {}).get("min", 50000)
    total_max = costs.get("total_range", {}).get("max", 100000)
    breakdown = costs.get("breakdown", [])

    tiers = []

    for tier_name, multipliers in TIER_MULTIPLIERS.items():
        min_cost = int(total_min * multipliers["min_multiplier"])
        max_cost = int(total_max * multipliers["max_multiplier"])

        # Break down by category
        line_items = []
        for item in breakdown:
            if isinstance(item, dict):
                line_items.append({
                    "category": item.get("category", ""),
                    "name": item.get("category", ""),
                    "min_cost": int(item.get("range", {}).get("min", 0) * multipliers["min_multiplier"]),
                    "max_cost": int(item.get("range", {}).get("max", 0) * multipliers["max_multiplier"]),
                    "notes": f"{item.get('items', '')} - adjusted for {tier_name}"
                })

        tiers.append({
            "tier": tier_name,
            "model": tier_name,
            "total_range": {
                "min": min_cost,
                "max": max_cost,
                "formatted": f"${min_cost/1000:.0f}k - ${max_cost/1000:.0f}k"
            },
            "philosophy": multipliers["philosophy"],
            "approach": multipliers["approach"],
            "team_size": multipliers["team_size"],
            "timeline_weeks": multipliers["timeline_weeks"],
            "line_items": line_items
        })

    logger.info(f"[SETUP] Generated {len(tiers)} cost tiers")
    return tiers


# ═══ SUPPLIERS (LLM + Cache) ═══

async def get_or_generate_suppliers(business_type: str, city: str, state: str, tier: str, customers: list[str]) -> list[dict]:
    """Get cached suppliers or generate via LLM."""

    # Check cache first
    cached = await get_cached_setup(business_type, city, state, tier, "suppliers")
    if cached:
        return cached

    logger.info(f"[SETUP] Generating suppliers for {business_type} in {city} ({tier} tier)")

    try:
        system_prompt = setup_suppliers_system()
        user_prompt = setup_suppliers_user(business_type, city, state, tier, customers)

        response = await call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.3,
            max_tokens=1500,
            json_mode=True,
        )

        suppliers = json.loads(response).get("suppliers", []) if isinstance(response, str) else response.get("suppliers", [])

        # Cache
        await cache_setup_data(business_type, city, state, tier, "suppliers", suppliers, ttl_days=60)

        return suppliers

    except Exception as e:
        logger.error(f"[SETUP] Suppliers generation failed: {e}")
        return []


# ═══ TEAM (LLM + Cache) ═══

async def get_or_generate_team(business_type: str, tier: str, root_causes: list[dict], costs: dict) -> list[dict]:
    """Get team plan via LLM."""

    logger.info(f"[SETUP] Generating team plan for {business_type} ({tier} tier)")

    try:
        total_cost = costs.get("total_range", {}).get("max", 100000)

        system_prompt = setup_team_system()
        user_prompt = setup_team_user(business_type, tier, root_causes, total_cost)

        response = await call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.3,
            max_tokens=1500,
            json_mode=True,
        )

        team = json.loads(response).get("team", []) if isinstance(response, str) else response.get("team", [])
        return team

    except Exception as e:
        logger.error(f"[SETUP] Team generation failed: {e}")
        return []


# ═══ TIMELINE (LLM + Cache) ═══

async def get_or_generate_timeline(business_type: str, tier: str, pain_intensity: float, root_causes: list[dict], costs: dict) -> list[dict]:
    """Generate timeline via LLM."""

    # Classify pain level
    pain_level = "high" if pain_intensity >= 7 else ("medium" if pain_intensity >= 4 else "low")
    logger.info(f"[SETUP] Generating timeline for {business_type} ({tier} tier, pain={pain_level})")

    try:
        total_cost = costs.get("total_range", {}).get("max", 100000)

        system_prompt = setup_timeline_system()
        user_prompt = setup_timeline_user(business_type, tier, pain_intensity, root_causes, total_cost)

        response = await call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.3,
            max_tokens=1500,
            json_mode=True,
        )

        timeline = json.loads(response).get("timeline", []) if isinstance(response, str) else response.get("timeline", [])
        return timeline

    except Exception as e:
        logger.error(f"[SETUP] Timeline generation failed: {e}")
        return []


# ═══ MAIN SETUP GENERATION ═══

async def generate_full_setup(decomposition: dict, costs: dict, root_causes: list[dict], customers: dict, selected_tier: str = "MID") -> dict:
    """Generate complete SETUP response with all 4 components."""

    business_type = decomposition.get("business_type", "")
    location = decomposition.get("location", {})
    city = location.get("city", "")
    state = location.get("state", "")
    target_customers = decomposition.get("target_customers", [])

    # Get pain intensity (max from customers segments)
    pain_intensity = 5.0  # Default
    if customers and "segments" in customers:
        segments = customers.get("segments", [])
        if segments:
            pain_intensity = max(seg.get("pain_intensity", 5) for seg in segments)

    logger.info(f"[SETUP] Generating full setup: {business_type} in {city} ({selected_tier} tier)")

    # 1. COST TIERS (deterministic, instant)
    cost_tiers = generate_cost_tiers(costs)

    # 2. SUPPLIERS (LLM + cache)
    suppliers = await get_or_generate_suppliers(business_type, city, state, selected_tier, target_customers)

    # 3. TEAM (LLM + cache)
    team = await get_or_generate_team(business_type, selected_tier, root_causes, costs)

    # 4. TIMELINE (LLM + cache)
    timeline = await get_or_generate_timeline(business_type, selected_tier, pain_intensity, root_causes, costs)

    return {
        "cost_tiers": cost_tiers,
        "suppliers": suppliers,
        "team": team,
        "timeline": timeline
    }
