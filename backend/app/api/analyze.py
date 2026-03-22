"""
POST /api/analyze-section
Generates one of five analysis sections on demand (lazy-loaded per tab click).
Sections: opportunity | customers | competitors | rootcause | costs
"""

import logging
from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import optional_user
from app.schemas.models import AnalyzeRequest, AnalyzeResponse
from app.services.llm_client import call_llm, AllProvidersExhaustedError
from app.services.google_search import run_search_queries, build_competitor_queries
from app.services.data_cleaner import clean_search_results
from app.prompts.templates import (
    analyze_opportunity_system, analyze_customers_system,
    analyze_competitors_system, analyze_rootcause_system,
    analyze_costs_preview_system, analyze_section_user,
)

logger = logging.getLogger(__name__)
router = APIRouter()

VALID_SECTIONS = {"opportunity", "customers", "competitors", "rootcause", "costs"}


@router.post("/api/analyze-section", response_model=AnalyzeResponse)
async def analyze_section(
    req: AnalyzeRequest,
    user: dict | None = Depends(optional_user),
):
    section = req.section.lower().strip()
    if section not in VALID_SECTIONS:
        raise HTTPException(status_code=400, detail=f"Invalid section: {section}. Must be one of: {VALID_SECTIONS}")

    decomp = req.decomposition.model_dump() if hasattr(req.decomposition, 'model_dump') else req.decomposition
    insight = req.insight.model_dump() if hasattr(req.insight, 'model_dump') else req.insight
    loc = decomp.get("location", {})
    city = loc.get("city", "")
    state = loc.get("state", "")
    metro = loc.get("metro", "")
    btype = decomp.get("business_type", "")

    handler = {
        "opportunity": _handle_opportunity,
        "customers": _handle_customers,
        "competitors": _handle_competitors,
        "rootcause": _handle_rootcause,
        "costs": _handle_costs,
    }[section]

    try:
        data = await handler(decomp, insight, btype, city, state, metro, req.prior_context)
    except AllProvidersExhaustedError:
        raise HTTPException(status_code=503, detail="All LLM providers unavailable")

    return AnalyzeResponse(section=section, data=data)


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

    raw = await call_llm(system_prompt=system, user_prompt=user_prompt, temperature=0.3, max_tokens=2000)

    # Post-processing: validate TAM > SAM > SOM
    tam_val = _extract_value(raw, "tam")
    sam_val = _extract_value(raw, "sam")
    som_val = _extract_value(raw, "som")

    if tam_val and sam_val and tam_val < sam_val:
        # Swap if LLM got confused
        raw["tam"], raw["sam"] = raw["sam"], raw["tam"]
    if sam_val and som_val and sam_val < som_val:
        raw["sam"], raw["som"] = raw["som"], raw["sam"]

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

    raw = await call_llm(system_prompt=system, user_prompt=user_prompt, temperature=0.3, max_tokens=2000)

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

    # Ingestion: 3-5 Serper queries for competitor data
    queries = build_competitor_queries(decomp)
    search_results = await run_search_queries(queries, location=f"{city}, {state}", num_per_query=8)
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
