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

TIER_ORDER = ["LEAN", "MID", "PREMIUM"]


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
            preferred_provider="groq",
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
            preferred_provider="groq",
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
            preferred_provider="groq",
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

    # 2-4. SUPPLIERS, TEAM, TIMELINE in PARALLEL (all independent LLM calls)
    import asyncio
    suppliers, team, timeline = await asyncio.gather(
        get_or_generate_suppliers(business_type, city, state, selected_tier, target_customers),
        get_or_generate_team(business_type, selected_tier, root_causes, costs),
        get_or_generate_timeline(business_type, selected_tier, pain_intensity, root_causes, costs)
    )

    recommendation = _recommend_setup_tier(cost_tiers, pain_intensity, root_causes, selected_tier)
    revenue_projection = _build_revenue_projection(cost_tiers, customers, selected_tier)
    founder_time_allocation = _build_founder_time_allocation(business_type, selected_tier)
    vendor_benchmarks = _build_vendor_benchmarks(suppliers, cost_tiers, selected_tier)

    return {
        "cost_tiers": cost_tiers,
        "suppliers": suppliers,
        "team": team,
        "timeline": timeline,
        "recommendation": recommendation,
        "revenue_projection": revenue_projection,
        "founder_time_allocation": founder_time_allocation,
        "vendor_benchmarks": vendor_benchmarks,
    }


def _recommend_setup_tier(cost_tiers: list[dict], pain_intensity: float, root_causes: list[dict], selected_tier: str) -> dict:
    tier_lookup = {tier["tier"]: tier for tier in cost_tiers}
    hard_causes = sum(1 for cause in root_causes if "hard" in str(cause.get("difficulty", "")).lower())

    recommended = "MID"
    rationale = "Balanced execution gives you the best chance to validate demand without overbuilding."

    if pain_intensity <= 4 and hard_causes >= 1:
        recommended = "LEAN"
        rationale = "Demand urgency is still moderate, so a lean launch lowers burn while you prove the core use case."
    elif pain_intensity >= 8 and hard_causes == 0:
        recommended = "PREMIUM"
        rationale = "Demand urgency is strong and execution complexity is manageable, so investing in a faster premium rollout is justified."
    elif hard_causes >= 2:
        recommended = "MID"
        rationale = "Execution complexity is elevated, so a balanced tier is safer than a premium burn profile."

    not_viable: list[str] = []
    premium_cost = tier_lookup.get("PREMIUM", {}).get("total_range", {}).get("max", 0)
    mid_cost = tier_lookup.get("MID", {}).get("total_range", {}).get("max", 0)
    if premium_cost and mid_cost and premium_cost > (mid_cost * 1.6):
        not_viable.append("PREMIUM")
    if pain_intensity <= 3:
        not_viable.append("PREMIUM")

    return {
        "selected_tier": selected_tier,
        "recommended_tier": recommended,
        "rationale": rationale,
        "not_recommended": list(dict.fromkeys(not_viable)),
    }


def _build_revenue_projection(cost_tiers: list[dict], customers: dict, selected_tier: str) -> dict:
    tier_lookup = {tier["tier"]: tier for tier in cost_tiers}
    current_tier = tier_lookup.get(selected_tier) or tier_lookup.get("MID") or {}
    total_max = float(current_tier.get("total_range", {}).get("max", 0) or 0)

    segments = customers.get("segments", []) if isinstance(customers, dict) else []
    if segments:
        avg_size = sum(float(seg.get("estimated_size", 0) or 0) for seg in segments) / len(segments)
        avg_pain = sum(float(seg.get("pain_intensity", 0) or 0) for seg in segments) / len(segments)
    else:
        avg_size = 50000
        avg_pain = 5

    monthly_revenue = int(max(4000, min(45000, (avg_size * 0.0025) * max(1.1, avg_pain / 3.5))))
    monthly_cost_base = max(3500, int(total_max / 18)) if total_max else 6000
    monthly_profit = monthly_revenue - monthly_cost_base
    if monthly_profit > 0 and total_max > 0:
        breakeven_months = max(1, round(total_max / monthly_profit))
    else:
        breakeven_months = None

    return {
        "expected_monthly_revenue": monthly_revenue,
        "expected_monthly_operating_cost": monthly_cost_base,
        "expected_monthly_profit": monthly_profit,
        "breakeven_months": breakeven_months,
        "breakeven_label": f"{breakeven_months} months" if breakeven_months else "Not under current assumptions",
    }


def _build_founder_time_allocation(business_type: str, selected_tier: str) -> list[dict]:
    lower_btype = (business_type or "").lower()
    if any(term in lower_btype for term in ["restaurant", "bar", "food", "juice", "cafe"]):
        allocation = {"ops": 45, "marketing": 25, "admin": 20, "partnerships": 10}
    elif any(term in lower_btype for term in ["software", "app", "platform", "saas"]):
        allocation = {"product": 35, "marketing": 30, "customer_research": 20, "admin": 15}
    else:
        allocation = {"ops": 40, "marketing": 30, "admin": 20, "customer_research": 10}

    if selected_tier == "LEAN":
        allocation = {k: v + (10 if k in {"ops", "product"} else -3) for k, v in allocation.items()}
    elif selected_tier == "PREMIUM":
        allocation = {k: v - (5 if k in {"ops", "product"} else 0) + (5 if k in {"marketing", "partnerships"} else 0) for k, v in allocation.items()}

    total = sum(allocation.values()) or 100
    return [
        {"area": area.replace("_", " ").title(), "percent": round((percent / total) * 100)}
        for area, percent in allocation.items()
    ]


def _build_vendor_benchmarks(suppliers: list[dict], cost_tiers: list[dict], selected_tier: str) -> list[dict]:
    tier_lookup = {tier["tier"]: tier for tier in cost_tiers}
    selected = tier_lookup.get(selected_tier) or {}
    line_items = selected.get("line_items", [])
    line_item_lookup = {item.get("category", "").lower(): item for item in line_items}

    benchmarks = []
    for supplier in suppliers[:6]:
        category = str(supplier.get("category", "")).lower()
        line_item = line_item_lookup.get(category)
        benchmark_cost = None
        if line_item:
            benchmark_cost = {
                "min": line_item.get("min_cost", 0),
                "max": line_item.get("max_cost", 0),
            }
        benchmarks.append({
            "vendor": supplier.get("name", ""),
            "category": supplier.get("category", ""),
            "location": supplier.get("location", ""),
            "benchmark_cost_range": benchmark_cost,
            "why_recommended": supplier.get("why_recommended", ""),
        })
    return benchmarks
