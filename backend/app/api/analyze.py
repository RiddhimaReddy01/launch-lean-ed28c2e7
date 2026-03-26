"""
POST /api/analyze-section
Generates one of eight analysis sections on demand (lazy-loaded per tab click).
Sections: opportunity | customers | competitors | rootcause | costs | risk | location | moat

Accepts two request formats:
1. Raw idea: {idea, section} - will call decompose + discover internally
2. Pre-computed: {section, decomposition, insight} - skips internal calls
"""

import logging
from copy import deepcopy
import math
from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import optional_user
from app.schemas.models import AnalyzeRequest, AnalyzeResponse
from app.services.llm_client import call_llm, AllProvidersExhaustedError
from app.services.google_search import run_search_queries, build_competitor_queries
from app.services.data_cleaner import clean_search_results
from app.prompts.templates import (
    analyze_opportunity_system, analyze_customers_system,
    analyze_competitors_system, analyze_rootcause_system,
    analyze_costs_preview_system, analyze_risk_system,
    analyze_location_system, analyze_moat_system, analyze_section_user,
)

logger = logging.getLogger(__name__)
router = APIRouter()

VALID_SECTIONS = {"opportunity", "customers", "competitors", "rootcause", "costs", "risk", "location", "moat"}


def _fallback_insight_from_decomp(decomp: dict) -> dict:
    """Create a minimal synthetic insight so downstream analysis can still run."""
    location = decomp.get("location", {}) or {}
    location_label = ", ".join(filter(None, [location.get("city", ""), location.get("state", "")])).strip(", ")
    business_type = decomp.get("business_type", "business idea")
    title = f"Baseline demand signals for {business_type}"
    if location_label:
        title += f" in {location_label}"

    return {
        "id": "fallback_insight",
        "type": "market_gap",
        "title": title,
        "score": 4.5,
        "mention_count": 0,
        "evidence": [
            {
                "quote": "Using decomposition-based fallback because discover insights were unavailable.",
                "source": "system",
                "score": 0,
            }
        ],
        "source_platforms": ["system"],
        "audience_estimate": "",
    }


@router.post("/api/analyze-section", response_model=AnalyzeResponse)
async def analyze_section(
    req: AnalyzeRequest,
    user: dict | None = Depends(optional_user),
):
    section = req.section.lower().strip()
    logger.info(f"Analyze request: section={section}, has_decomposition={req.decomposition is not None}, has_insight={req.insight is not None}")

    if section not in VALID_SECTIONS:
        error_msg = f"Invalid section: {section}. Must be one of: {VALID_SECTIONS}"
        logger.error(error_msg)
        raise HTTPException(status_code=400, detail=error_msg)

    # Handle two request formats:
    # 1. Pre-computed (from Lovable frontend): decomposition + insight provided, skip internal calls
    # 2. Raw idea: call decompose + discover internally

    if req.decomposition and req.insight:
        # Format 1: Pre-computed data from frontend - skip internal API calls
        logger.info(f"Using pre-computed decomposition and insight")
        decomp = req.decomposition
        insight = req.insight
    elif req.idea:
        # Format 2: Raw idea string - call decompose + discover internally
        logger.info(f"Calling decompose + discover internally for idea")
        from app.api.decompose import decompose_idea
        from app.api.discover import discover_insights
        from app.schemas.models import DecomposeRequest, DiscoverRequest

        decompose_req = DecomposeRequest(idea=req.idea)
        decomp_response = await decompose_idea(decompose_req, user=user)
        decomp = decomp_response.model_dump() if hasattr(decomp_response, 'model_dump') else decomp_response

        discover_req = DiscoverRequest(idea=req.idea)
        discover_response = await discover_insights(discover_req, user=user)
        discover_data = discover_response.model_dump() if hasattr(discover_response, 'model_dump') else discover_response

        insights = discover_data.get("insights", [])
        insight = insights[0] if insights else _fallback_insight_from_decomp(decomp)
    else:
        raise HTTPException(status_code=400, detail="Provide either 'idea' or 'decomposition+insight'")

    # Extract location details
    loc = decomp.get("location", {})
    city = loc.get("city", "")
    state = loc.get("state", "")
    metro = loc.get("metro", "")
    btype = decomp.get("business_type", "")

    # Dispatch to appropriate handler
    handler = {
        "opportunity": _handle_opportunity,
        "customers": _handle_customers,
        "competitors": _handle_competitors,
        "rootcause": _handle_rootcause,
        "costs": _handle_costs,
        "risk": _handle_risk,
        "location": _handle_location,
        "moat": _handle_moat,
    }[section]

    try:
        data = await handler(decomp, insight, btype, city, state, metro, req.prior_context)
    except AllProvidersExhaustedError:
        raise HTTPException(status_code=503, detail="All LLM providers unavailable")

    synthesis = _build_analysis_synthesis(section, data, req.prior_context, insight, decomp)
    if synthesis and section == "opportunity":
        data = {**data, "synthesis": synthesis}

    return AnalyzeResponse(section=section, data=data, synthesis=synthesis)


# ═══ SECTION HANDLERS ═══


async def _handle_opportunity(
    decomp: dict, insight: dict, btype: str,
    city: str, state: str, metro: str,
    prior_context: dict | None,
) -> dict:
    """Section A: TAM / SAM / SOM market sizing."""

    # Ingestion: 2-3 Serper queries for market data
    queries = [
        f"{btype} market size {metro}",
        f"{btype} industry report 2025 2026",
        f"average revenue {btype} {state}",
    ]
    search_results = await run_search_queries(queries, location=f"{city}, {state}", num_per_query=5)
    cleaned = clean_search_results(search_results, query_type="market_data")

    # Build extra context from search
    market_context = "\n".join(
        f"- {r['title']}: {r['snippet']}" for r in cleaned[:10]
    )

    # LLM call
    system = analyze_opportunity_system(btype, city, state, metro)
    user_prompt = analyze_section_user("opportunity", insight, decomp, market_context)

    raw = await call_llm(system_prompt=system, user_prompt=user_prompt, temperature=0.3, max_tokens=2000, preferred_provider="groq")

    # Post-processing: validate TAM > SAM > SOM
    tam_val = _extract_value(raw, "tam")
    sam_val = _extract_value(raw, "sam")
    som_val = _extract_value(raw, "som")

    if tam_val and sam_val and tam_val < sam_val and "tam" in raw and "sam" in raw:
        # Swap if LLM got confused
        raw["tam"], raw["sam"] = raw["sam"], raw["tam"]
    if sam_val and som_val and sam_val < som_val and "sam" in raw and "som" in raw:
        raw["sam"], raw["som"] = raw["som"], raw["sam"]

    # Ensure funnel is never null (fix frontend crash)
    if "funnel" not in raw or not raw["funnel"]:
        raw["funnel"] = {
            "population": 0,
            "aware": 0,
            "interested": 0,
            "willing_to_try": 0,
            "repeat_customers": 0
        }

    return raw


async def _handle_customers(
    decomp: dict, insight: dict, btype: str,
    city: str, state: str, metro: str,
    prior_context: dict | None,
) -> dict:
    """Section B: Customer segmentation with pain intensity."""

    # No new ingestion - uses existing evidence
    system = analyze_customers_system(btype, city)
    user_prompt = analyze_section_user("customers", insight, decomp)

    raw = await call_llm(system_prompt=system, user_prompt=user_prompt, temperature=0.3, max_tokens=2000, preferred_provider="groq")

    # Post-processing
    segments = raw.get("segments", [])

    # Validate 3-4 segments
    if len(segments) < 3:
        logger.warning(f"Only {len(segments)} segments returned, expected 3-4")
    segments = segments[:4]

    # Normalize pain_intensity to 1-10
    for seg in segments:
        pi = seg.get("pain_intensity", 5)
        if isinstance(pi, (int, float)):
            seg["pain_intensity"] = min(10, max(1, round(pi)))

    # Sort by pain_intensity descending
    segments.sort(key=lambda s: s.get("pain_intensity", 0), reverse=True)
    raw["segments"] = segments

    return raw


async def _handle_competitors(
    decomp: dict, insight: dict, btype: str,
    city: str, state: str, metro: str,
    prior_context: dict | None,
) -> dict:
    """Section C: Competitive landscape with gaps."""

    # Ingestion: Competitor data from Serper
    queries = build_competitor_queries(decomp)[:3]  # Limit to first 3 queries
    search_results = await run_search_queries(queries, location=f"{city}, {state}", num_per_query=5)  # Reduced for speed
    cleaned = clean_search_results(search_results, query_type="competitors")

    competitor_context = "\n".join(
        f"- {r['title']} | {r['snippet'][:200]} | Rating: {r.get('rating', 'N/A')} | {r['link']}"
        for r in cleaned[:20]
    )

    # LLM call
    system = analyze_competitors_system(btype, city, state)
    user_prompt = analyze_section_user("competitors", insight, decomp, competitor_context)

    raw = await call_llm(system_prompt=system, user_prompt=user_prompt, temperature=0.3, max_tokens=3000)

    # Post-processing
    competitors = raw.get("competitors", [])

    # Validate 4-8 competitors
    competitors = competitors[:8]

    # Validate threat_level
    valid_threats = {"low", "medium", "high"}
    for c in competitors:
        if c.get("threat_level", "").lower() not in valid_threats:
            c["threat_level"] = "medium"

    # Sort by threat_level (high first)
    threat_order = {"high": 0, "medium": 1, "low": 2}
    competitors.sort(key=lambda c: threat_order.get(c.get("threat_level", "medium"), 1))
    raw["competitors"] = competitors

    return raw


async def _handle_rootcause(
    decomp: dict, insight: dict, btype: str,
    city: str, state: str, metro: str,
    prior_context: dict | None,
) -> dict:
    """Section D: Root cause analysis - the most differentiated section."""

    # No new ingestion - uses all accumulated context
    extra = ""
    if prior_context:
        if "competitors" in prior_context:
            comps = prior_context["competitors"].get("competitors", [])
            extra += "Competitors:\n" + "\n".join(
                f"- {c.get('name', '')}: Gap = {c.get('key_gap', '')}" for c in comps[:6]
            )
        if "customers" in prior_context:
            segs = prior_context["customers"].get("segments", [])
            extra += "\n\nCustomer segments:\n" + "\n".join(
                f"- {s.get('name', '')}: Pain = {s.get('primary_need', '')}" for s in segs[:4]
            )
        if "opportunity" in prior_context:
            opp = prior_context["opportunity"]
            som = opp.get("som", {})
            extra += f"\n\nSOM estimate: {som.get('formatted', 'unknown')}"

    system = analyze_rootcause_system(btype, city, state)
    user_prompt = analyze_section_user("rootcause", insight, decomp, extra)

    raw = await call_llm(
        system_prompt=system, user_prompt=user_prompt,
        temperature=0.5,  # Higher creativity for strategic reasoning
        max_tokens=3000,
    )

    # Post-processing
    causes = raw.get("root_causes", [])

    # Validate 3-5 root causes
    causes = causes[:5]
    if len(causes) < 3:
        logger.warning(f"Only {len(causes)} root causes returned, expected 3-5")

    # Validate difficulty and ensure your_move is non-empty
    valid_diff = {"easy", "medium", "hard"}
    for c in causes:
        if c.get("difficulty", "").lower() not in valid_diff:
            c["difficulty"] = "medium"
        if not c.get("your_move"):
            c["your_move"] = "Research this further before launch."

    # Sort by difficulty (easy first - quick wins for founder)
    diff_order = {"easy": 0, "medium": 1, "hard": 2}
    causes.sort(key=lambda c: diff_order.get(c.get("difficulty", "medium"), 1))
    raw["root_causes"] = causes

    return raw


async def _handle_costs(
    decomp: dict, insight: dict, btype: str,
    city: str, state: str, metro: str,
    prior_context: dict | None,
) -> dict:
    """Section E: Cost preview (teaser for Module 3)."""

    system = analyze_costs_preview_system(btype, city, state)
    user_prompt = analyze_section_user("costs", insight, decomp)

    raw = await call_llm(system_prompt=system, user_prompt=user_prompt, temperature=0.3, max_tokens=1000)

    # Post-processing: format as min/max range
    total = raw.get("total_range", {})
    if isinstance(total, dict):
        mn = total.get("min", 0)
        mx = total.get("max", 0)
        if mn > mx:
            total["min"], total["max"] = mx, mn
        raw["total_range"] = total

    return raw


async def _handle_risk(
    decomp: dict, insight: dict, btype: str,
    city: str, state: str, metro: str,
    prior_context: dict | None,
) -> dict:
    """Section: Risk assessment - key risks that could derail the business."""

    system = analyze_risk_system(btype, city, state)
    user_prompt = analyze_section_user("risk", insight, decomp)

    raw = await call_llm(system_prompt=system, user_prompt=user_prompt, temperature=0.5, max_tokens=2000)

    # Post-processing
    risks = raw.get("risks", [])
    risks = risks[:5]  # Cap at 5 risks

    # Validate impact and likelihood values
    valid_levels = {"high", "medium", "low"}
    for r in risks:
        if r.get("impact", "").lower() not in valid_levels:
            r["impact"] = "medium"
        if r.get("likelihood", "").lower() not in valid_levels:
            r["likelihood"] = "medium"

    # Sort by impact * likelihood (high impact + high likelihood first)
    priority_order = {"high": 0, "medium": 1, "low": 2}
    risks.sort(key=lambda r: (
        priority_order.get(r.get("impact", "medium").lower(), 1) +
        priority_order.get(r.get("likelihood", "medium").lower(), 1)
    ))
    raw["risks"] = risks

    return raw


async def _handle_location(
    decomp: dict, insight: dict, btype: str,
    city: str, state: str, metro: str,
    prior_context: dict | None,
) -> dict:
    """Section: Location-specific insights - geographic advantages and challenges."""

    system = analyze_location_system(btype, city, state)
    user_prompt = analyze_section_user("location", insight, decomp)

    raw = await call_llm(system_prompt=system, user_prompt=user_prompt, temperature=0.4, max_tokens=2000)

    # Post-processing
    analyses = raw.get("location_analysis", [])
    analyses = analyses[:4]  # Cap at 4 aspects

    # Validate overall_viability
    valid_viability = {"high", "medium", "low"}
    if raw.get("overall_viability", "").lower() not in valid_viability:
        raw["overall_viability"] = "medium"

    raw["city_center"] = _city_center_point(city, state)
    raw["focus_areas"] = _build_focus_areas(
        raw.get("focus_areas", []),
        city,
        state,
        analyses,
    )

    raw["location_analysis"] = analyses
    return raw


async def _handle_moat(
    decomp: dict, insight: dict, btype: str,
    city: str, state: str, metro: str,
    prior_context: dict | None,
) -> dict:
    """Section: Competitive moat - sustainable advantages and defensibility."""

    system = analyze_moat_system(btype, city, state)
    user_prompt = analyze_section_user("moat", insight, decomp)

    raw = await call_llm(system_prompt=system, user_prompt=user_prompt, temperature=0.5, max_tokens=2000)

    # Post-processing
    elements = raw.get("moat_elements", [])
    elements = elements[:4]  # Cap at 4 moat elements

    # Validate strength values
    valid_strengths = {"strong", "moderate", "weak"}
    for elem in elements:
        if elem.get("strength", "").lower() not in valid_strengths:
            elem["strength"] = "moderate"

    # Validate defensibility
    valid_defensibility = {"high", "medium", "low"}
    if raw.get("overall_defensibility", "").lower() not in valid_defensibility:
        raw["overall_defensibility"] = "medium"

    raw["moat_elements"] = elements
    return raw


# ═══ HELPERS ═══


def _extract_value(data: dict, key: str) -> float | None:
    """Extract numeric value from a nested market size field."""
    item = data.get(key, {})
    if isinstance(item, dict):
        v = item.get("value", item.get("dollar_figure", 0))
        try:
            return float(v)
        except (TypeError, ValueError):
            return None
    return None


def _build_analysis_synthesis(
    section: str,
    current_data: dict,
    prior_context: dict | None,
    insight: dict,
    decomp: dict,
) -> dict:
    combined = deepcopy(prior_context or {})
    combined[section] = current_data

    opportunity = combined.get("opportunity", {})
    customers = combined.get("customers", {})
    competitors = combined.get("competitors", {})
    costs = combined.get("costs", {})
    risk = combined.get("risk", {})
    rootcause = combined.get("rootcause", {})

    som_value = float(opportunity.get("som", {}).get("value", 0) or 0)
    customer_segments = customers.get("segments", []) or []
    competitor_list = competitors.get("competitors", []) or []
    unfilled_gaps = competitors.get("unfilled_gaps", []) or []
    risk_items = risk.get("risks", []) or []
    root_causes = rootcause.get("root_causes", []) or []

    avg_pain = (
        sum(float(seg.get("pain_intensity", 0) or 0) for seg in customer_segments) / len(customer_segments)
        if customer_segments else float(insight.get("intensity_score", 0) or 0)
    )
    competitor_pressure = sum(
        1.0 if c.get("threat_level") == "high" else 0.5 if c.get("threat_level") == "medium" else 0.2
        for c in competitor_list
    )
    high_risk_count = sum(
        1 for r in risk_items
        if str(r.get("impact", "")).lower() == "high" or str(r.get("likelihood", "")).lower() == "high"
    )
    top_gap_count = min(len(unfilled_gaps), 3)

    som_score = 0
    if som_value >= 25_000_000:
        som_score = 28
    elif som_value >= 10_000_000:
        som_score = 22
    elif som_value >= 3_000_000:
        som_score = 16
    elif som_value > 0:
        som_score = 10

    pain_score = min(24, max(0, avg_pain * 2.4))
    gap_score = min(18, top_gap_count * 6)
    competition_penalty = min(18, competitor_pressure * 4)
    risk_penalty = min(16, high_risk_count * 4)

    opportunity_score = round(max(0, min(100, 32 + som_score + pain_score + gap_score - competition_penalty - risk_penalty)))

    evidence_points = 0
    if som_value:
        evidence_points += 1
    if customer_segments:
        evidence_points += 1
    if competitor_list:
        evidence_points += 1
    if risk_items:
        evidence_points += 1
    if root_causes:
        evidence_points += 1
    confidence = "high" if evidence_points >= 4 else "medium" if evidence_points >= 2 else "low"

    repeat_customers = float(opportunity.get("funnel", {}).get("repeat_customers", 0) or 0)
    interested = float(opportunity.get("funnel", {}).get("interested", 0) or 0)
    retention_ratio = (repeat_customers / interested) if interested else 0

    if opportunity_score >= 75 and high_risk_count <= 1:
        final_verdict = "build"
    elif opportunity_score <= 45 or high_risk_count >= 3:
        final_verdict = "avoid"
    else:
        final_verdict = "modify"

    top_drivers = _rank_top_drivers(customer_segments, unfilled_gaps, competitor_list, root_causes)
    tradeoff_reasoning = _build_tradeoff_reasoning(avg_pain, retention_ratio, competitor_pressure, high_risk_count, unfilled_gaps)
    sensitivity_analysis = _build_sensitivity_analysis(costs, opportunity, avg_pain)

    return {
        "final_verdict": final_verdict,
        "opportunity_score": opportunity_score,
        "confidence": confidence,
        "key_insight": tradeoff_reasoning,
        "tradeoff_reasoning": tradeoff_reasoning,
        "top_drivers": top_drivers,
        "sensitivity_analysis": sensitivity_analysis,
        "summary": _build_synthesis_summary(final_verdict, opportunity_score, confidence, top_drivers, decomp),
    }


def _rank_top_drivers(customer_segments: list[dict], gaps: list[str], competitors: list[dict], root_causes: list[dict]) -> list[str]:
    drivers: list[tuple[float, str]] = []
    for seg in customer_segments[:3]:
        pain = float(seg.get("pain_intensity", 0) or 0)
        primary_need = seg.get("primary_need") or seg.get("name") or "Customer pain"
        drivers.append((pain + 2, primary_need))
    for gap in gaps[:3]:
        drivers.append((7.5, gap))
    low_comp_count = sum(1 for c in competitors if str(c.get("threat_level", "")).lower() == "low")
    if low_comp_count:
        drivers.append((6.5 + low_comp_count, "Limited strong competition in the target segment"))
    for cause in root_causes[:2]:
        move = cause.get("your_move") or cause.get("title") or ""
        if move:
            drivers.append((6.0, move))

    deduped: list[str] = []
    for _, text in sorted(drivers, key=lambda item: item[0], reverse=True):
        normalized = text.strip()
        if normalized and normalized not in deduped:
            deduped.append(normalized)
    return deduped[:3]


def _build_tradeoff_reasoning(
    avg_pain: float,
    retention_ratio: float,
    competitor_pressure: float,
    high_risk_count: int,
    gaps: list[str],
) -> str:
    if avg_pain >= 7 and retention_ratio < 0.2:
        return "High demand exists, but repeat behavior looks weak. Prioritize retention and repeat usage before scaling acquisition."
    if avg_pain >= 7 and competitor_pressure >= 3:
        return "Demand is real, but competitive pressure is high. Differentiation matters more than raw market size."
    if gaps and high_risk_count <= 1:
        return f"The clearest upside is {gaps[0]}. The business looks most attractive if you focus the launch tightly around that opening."
    if high_risk_count >= 3:
        return "The market has potential, but operational and execution risks are doing most of the damage right now."
    return "The opportunity is viable, but the biggest advantage will come from disciplined positioning rather than broad expansion."


def _build_sensitivity_analysis(costs: dict, opportunity: dict, avg_pain: float) -> list[dict]:
    total_max = float(costs.get("total_range", {}).get("max", 0) or 0)
    monthly_base = max(3000.0, total_max / 12 if total_max else 5000.0)
    repeat_customers = float(opportunity.get("funnel", {}).get("repeat_customers", 0) or 0)
    willing_to_try = float(opportunity.get("funnel", {}).get("willing_to_try", 0) or 0)
    base_revenue = max(repeat_customers * 45, willing_to_try * 12)

    cac_impact = round(((base_revenue - (monthly_base * 1.3)) - (base_revenue - monthly_base)) / max(base_revenue, 1) * 100)
    retention_revenue = round(((base_revenue * 2.0) - base_revenue) / max(base_revenue, 1) * 100)
    demand_drop = round((avg_pain / 10) * 25)

    return [
        {
            "scenario": "If CAC increases by 30%",
            "impact": f"Estimated monthly profitability drops by about {abs(cac_impact)}%",
        },
        {
            "scenario": "If retention improves by 20%",
            "impact": f"Estimated recurring revenue could increase by about {retention_revenue}%",
        },
        {
            "scenario": "If demand intensity softens",
            "impact": f"Expected conversion to repeat customers may fall by roughly {demand_drop}%",
        },
    ]


def _build_synthesis_summary(verdict: str, score: int, confidence: str, top_drivers: list[str], decomp: dict) -> str:
    business_type = decomp.get("business_type", "idea")
    lead_driver = top_drivers[0] if top_drivers else "customer demand"
    return (
        f"For this {business_type}, the current recommendation is {verdict.upper()} "
        f"with an opportunity score of {score}/100 and {confidence} confidence. "
        f"The strongest driver is {lead_driver}."
    )


CITY_COORDINATES = {
    ("plano", "texas"): (33.0198, -96.6989),
    ("dallas", "texas"): (32.7767, -96.7970),
    ("austin", "texas"): (30.2672, -97.7431),
    ("houston", "texas"): (29.7604, -95.3698),
    ("san francisco", "california"): (37.7749, -122.4194),
    ("new york", "new york"): (40.7128, -74.0060),
    ("chicago", "illinois"): (41.8781, -87.6298),
    ("seattle", "washington"): (47.6062, -122.3321),
}


def _city_center_point(city: str, state: str) -> dict:
    key = (str(city or "").lower(), str(state or "").lower())
    lat, lng = CITY_COORDINATES.get(key, (39.8283, -98.5795))
    label = ", ".join(part for part in [city, state] if part)
    return {"lat": lat, "lng": lng, "label": label or "Target market"}


def _build_focus_areas(focus_areas: list[dict], city: str, state: str, analyses: list[dict]) -> list[dict]:
    center = _city_center_point(city, state)
    names = []
    for area in focus_areas[:4]:
        name = area.get("name")
        if name:
            names.append({
                "name": name,
                "reason": area.get("reason", ""),
                "emphasis": area.get("emphasis", "medium"),
            })

    if not names:
        for idx, analysis in enumerate(analyses[:3]):
            aspect = analysis.get("aspect", "Focus area")
            names.append({
                "name": f"{city} {aspect}".strip(),
                "reason": analysis.get("opportunity") or analysis.get("recommendation") or analysis.get("observation", ""),
                "emphasis": "high" if idx == 0 else "medium",
            })

    positioned = []
    radii = [0.045, 0.035, 0.055, 0.028]
    for idx, area in enumerate(names[:4]):
        angle = (idx / max(1, len(names))) * (2 * math.pi)
        radius = radii[idx % len(radii)]
        lat = center["lat"] + (math.sin(angle) * radius)
        lng = center["lng"] + (math.cos(angle) * radius)
        positioned.append({
            "name": area["name"],
            "lat": round(lat, 4),
            "lng": round(lng, 4),
            "reason": area["reason"][:180],
            "emphasis": area.get("emphasis", "medium"),
        })
    return positioned
