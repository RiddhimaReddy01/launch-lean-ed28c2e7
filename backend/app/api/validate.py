"""
POST /api/generate-validation
Generates validation toolkit: landing page copy, survey, WhatsApp message, communities.
Uses accumulated context from ALL prior modules for contextual threading.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import optional_user
from app.schemas.models import (
    ValidateRequest, ValidateResponse,
    LandingPage, Survey, SurveyQuestion,
    WhatsAppMessage, Community, Scorecard,
)
from app.services.llm_client import call_llm, AllProvidersExhaustedError
from app.services.google_search import run_search_queries, build_community_queries
from app.services.data_cleaner import clean_search_results
from app.prompts.templates import validate_system, validate_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/api/generate-validation", response_model=ValidateResponse)
async def generate_validation(
    req: ValidateRequest,
    user: dict | None = Depends(optional_user),
):
    decomp = req.decomposition.model_dump() if hasattr(req.decomposition, 'model_dump') else req.decomposition
    insight = req.insight.model_dump() if hasattr(req.insight, 'model_dump') else req.insight
    loc = decomp.get("location", {})
    city = loc.get("city", "")
    state = loc.get("state", "")
    btype = decomp.get("business_type", "")
    channels = req.channels or ["landing_page", "survey"]

    # ═══ STAGE 1: DATA INGESTION ═══
    # Only community discovery requires new external data
    queries = build_community_queries(decomp)
    search_results = await run_search_queries(queries, location=f"{city}, {state}", num_per_query=8)

    # ═══ STAGE 2: DATA CLEANING ═══
    cleaned_communities = clean_search_results(search_results, query_type="communities")

    # ═══ STAGE 3: DATA TRANSFORMATION ═══
    # Extract pain language from Module 1 evidence
    pain_language = _extract_pain_language(insight)

    # Build analysis summary from Module 2
    analysis_summary = _build_analysis_summary(req.analysis_context)

    # Build setup summary from Module 3
    setup_summary = _build_setup_summary(req.setup_context)

    # Community search data
    community_context = "\n".join(
        f"- {r['title']}: {r['snippet'][:200]} ({r['link']})"
        for r in cleaned_communities[:15]
    )

    # ═══ STAGE 4: LLM LOGIC ═══
    system = validate_system(btype, city, state)
    user_prompt = validate_user(
        decomposition=decomp,
        insight=insight,
        pain_language=pain_language,
        analysis_summary=analysis_summary,
        setup_summary=setup_summary,
        community_search_data=community_context,
        channels=channels,
    )

    try:
        raw = await call_llm(
            system_prompt=system,
            user_prompt=user_prompt,
            temperature=0.6,  # Higher creativity for copywriting
            max_tokens=4000,
            json_mode=True,
            preferred_provider="groq",
        )
    except AllProvidersExhaustedError:
        raise HTTPException(status_code=503, detail="All LLM providers unavailable")

    # ═══ STAGE 5: POST-PROCESSING ═══
    return _post_process(raw, channels)


def _extract_pain_language(insight: dict) -> list[str]:
    """Extract actual customer quotes from insight evidence for use in copy."""
    quotes = []
    for ev in insight.get("evidence", []):
        quote = ev.get("quote", "")
        if quote and len(quote) > 10:
            quotes.append(quote)

    # Also use the insight title as a pain phrase
    title = insight.get("title", "")
    if title:
        quotes.insert(0, title)

    return quotes[:10]


def _build_analysis_summary(analysis_context: dict | None) -> str:
    """Build condensed analysis summary from Module 2 data."""
    if not analysis_context:
        return "No prior analysis available."

    parts = []
    if "opportunity" in analysis_context:
        opp = analysis_context["opportunity"]
        som = opp.get("som", {})
        parts.append(f"Market SOM: {som.get('formatted', 'unknown')}")

    if "competitors" in analysis_context:
        gaps = analysis_context["competitors"].get("unfilled_gaps", [])
        if gaps:
            parts.append(f"Unfilled gaps: {'; '.join(gaps[:3])}")

    if "rootcause" in analysis_context:
        causes = analysis_context["rootcause"].get("root_causes", [])
        moves = [c.get("your_move", "") for c in causes[:3] if c.get("your_move")]
        if moves:
            parts.append(f"Strategic moves: {'; '.join(moves)}")

    if "customers" in analysis_context:
        segs = analysis_context["customers"].get("segments", [])
        if segs:
            top_seg = segs[0]
            parts.append(f"Primary segment: {top_seg.get('name', 'unknown')} ({top_seg.get('primary_need', '')})")

    return "\n".join(parts) if parts else "No prior analysis available."


def _build_setup_summary(setup_context: dict | None) -> str:
    """Build condensed setup summary from Module 3 data."""
    if not setup_context:
        return "No setup data available."

    parts = []
    tiers = setup_context.get("cost_tiers", [])
    if tiers:
        for tier in tiers:
            tr = tier.get("total_range", {})
            parts.append(f"{tier.get('tier', 'unknown')}: ${tr.get('min', 0):,.0f}-${tr.get('max', 0):,.0f}")

    timeline = setup_context.get("timeline", [])
    if timeline:
        total_weeks = sum(_parse_weeks(p.get("weeks", "0")) for p in timeline)
        parts.append(f"Total timeline: ~{total_weeks} weeks")

    return "\n".join(parts) if parts else "No setup data available."


def _parse_weeks(weeks_str: str) -> int:
    """Parse '3-6' or '12' into max week number."""
    import re
    nums = re.findall(r"\d+", str(weeks_str))
    return int(nums[-1]) if nums else 0


def _post_process(raw: dict, channels: list[str]) -> ValidateResponse:
    """Validate and format the final validation toolkit response."""

    # ── Landing Page ──
    landing_page = None
    if "landing_page" in channels:
        lp = raw.get("landing_page", {})
        if lp:
            benefits = lp.get("benefits", [])
            if isinstance(benefits, str):
                benefits = [benefits]
            landing_page = LandingPage(
                headline=lp.get("headline", ""),
                subheadline=lp.get("subheadline", ""),
                benefits=benefits[:4],
                cta_text=lp.get("cta_text", "Join the waitlist"),
                social_proof_quote=lp.get("social_proof_quote", ""),
            )

    # ── Survey ──
    survey = None
    if "survey" in channels:
        sv = raw.get("survey", {})
        if sv:
            questions = []
            for q in sv.get("questions", [])[:7]:
                options = q.get("options")
                if isinstance(options, list) and len(options) == 0:
                    options = None
                questions.append(SurveyQuestion(
                    number=q.get("number", 0),
                    question=q.get("question", ""),
                    type=_normalize_question_type(q.get("type", "open_text")),
                    options=options,
                ))
            survey = Survey(
                title=sv.get("title", "Quick Survey"),
                questions=questions,
            )

    # ── WhatsApp ──
    whatsapp = None
    if "whatsapp" in channels:
        wa = raw.get("whatsapp_message", {})
        if wa:
            message = wa.get("message", "")
            # Ensure [SURVEY_LINK] placeholder is present
            if "[SURVEY_LINK]" not in message and message:
                message += "\n\nTake our quick survey: [SURVEY_LINK]"
            whatsapp = WhatsAppMessage(
                message=message,
                tone_note=wa.get("tone_note", ""),
            )

    # ── Communities ──
    communities = []
    for c in raw.get("communities", [])[:10]:
        communities.append(Community(
            name=c.get("name", ""),
            platform=_normalize_platform(c.get("platform", "other")),
            member_count=c.get("member_count"),
            rationale=c.get("rationale", ""),
            link=c.get("link", ""),
        ))

    # ── Scorecard ──
    sc = raw.get("scorecard", {})
    scorecard = Scorecard(
        waitlist_target=sc.get("waitlist_target", 150),
        survey_target=sc.get("survey_target", 50),
        switch_pct_target=sc.get("switch_pct_target", 60),
        price_tolerance_target=sc.get("price_tolerance_target", ""),
    )

    return ValidateResponse(
        landing_page=landing_page,
        survey=survey,
        whatsapp_message=whatsapp,
        communities=communities,
        scorecard=scorecard,
    )


def _normalize_question_type(t: str) -> str:
    valid = {"multiple_choice", "scale", "open_text", "email", "yes_no"}
    t = t.lower().strip().replace(" ", "_").replace("-", "_")
    return t if t in valid else "open_text"


def _normalize_platform(p: str) -> str:
    valid = {"facebook", "discord", "nextdoor", "reddit", "linkedin", "whatsapp", "other"}
    p = p.lower().strip()
    return p if p in valid else "other"
