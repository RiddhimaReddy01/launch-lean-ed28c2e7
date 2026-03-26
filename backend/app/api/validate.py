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
    WhatsAppMessage, Community, Scorecard, ValidationStrategy,
)
from app.services.llm_client import call_llm, AllProvidersExhaustedError
from app.services.google_search import run_search_queries, build_community_queries
from app.services.data_cleaner import clean_search_results
from app.prompts.templates import validate_system, validate_user

logger = logging.getLogger(__name__)
router = APIRouter()


def _fallback_insight_from_decomp(decomp: dict) -> dict:
    """Create a minimal insight so validation can still produce assets."""
    location = decomp.get("location", {}) or {}
    location_label = ", ".join(filter(None, [location.get("city", ""), location.get("state", "")])).strip(", ")
    business_type = decomp.get("business_type", "business idea")
    title = f"Baseline validation plan for {business_type}"
    if location_label:
        title += f" in {location_label}"

    return {
        "id": "fallback_insight",
        "type": "market_gap",
        "title": title,
        "score": 4.0,
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


@router.post("/api/generate-validation", response_model=ValidateResponse)
async def generate_validation(
    req: ValidateRequest,
    user: dict | None = Depends(optional_user),
):
    # Prefer upstream context from the caller; only recompute if it is missing.
    if req.decomposition:
        decomp = req.decomposition
    elif req.idea:
        from app.api.decompose import decompose_idea
        from app.schemas.models import DecomposeRequest

        decompose_req = DecomposeRequest(idea=req.idea)
        decomp_response = await decompose_idea(decompose_req, user=user)
        decomp = decomp_response.model_dump() if hasattr(decomp_response, 'model_dump') else decomp_response
    else:
        raise HTTPException(status_code=400, detail="Provide either 'idea' or 'decomposition'")

    insight = req.insight
    if not insight:
        discover_data = req.discover
        if not discover_data and req.idea:
            from app.api.discover import discover_insights
            from app.schemas.models import DiscoverRequest

            discover_req = DiscoverRequest(idea=req.idea, decomposition=decomp)
            discover_response = await discover_insights(discover_req, user=user)
            discover_data = discover_response.model_dump() if hasattr(discover_response, 'model_dump') else discover_response

        insights = (discover_data or {}).get("insights", [])
        insight = insights[0] if insights else _fallback_insight_from_decomp(decomp)

    loc = decomp.get("location", {})
    city = loc.get("city", "")
    state = loc.get("state", "")
    btype = decomp.get("business_type", "")
    channels = req.channels or ["landing_page", "survey"]

    # ═══ STAGE 1: DATA INGESTION ═══
    # Only community discovery requires new external data
    queries = build_community_queries(decomp)[:2]  # Limit to first 2 queries
    search_results = await run_search_queries(queries, location=f"{city}, {state}", num_per_query=5)  # Reduced for speed

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
    system = validate_system(btype, city, state, channels)
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
    def _extract_number(value, default, as_int=False):
        """Extract number from string or value (LLM may return 'Above $45...')"""
        if not value:
            return default
        try:
            if isinstance(value, str):
                # Extract first number from string
                import re
                match = re.search(r'(\d+\.?\d*)', value)
                num = float(match.group(1)) if match else default
            else:
                num = float(value)
            return int(num) if as_int else num
        except (ValueError, AttributeError):
            return default

    sc = raw.get("scorecard", {})
    scorecard = Scorecard(
        waitlist_target=_extract_number(sc.get("waitlist_target"), 50, as_int=True),
        survey_target=_extract_number(sc.get("survey_target"), 10, as_int=True),
        switch_pct_target=_extract_number(sc.get("switch_pct_target"), 60, as_int=True),
        price_tolerance_target=_extract_number(sc.get("price_tolerance_target"), 12.0),
        paid_signups_target=_extract_number(sc.get("paid_signups_target"), 5, as_int=True),
        ltv_cac_ratio_target=_extract_number(sc.get("ltv_cac_ratio_target"), 3.0),
        is_custom=bool(sc.get("is_custom", False)),
    )

    strategy = _build_validation_strategy(channels, scorecard)
    expected_outcomes = _build_expected_outcomes(channels, scorecard)
    simulation = _build_simulation(channels, scorecard)
    recommended_sequence = _build_recommended_sequence(channels)

    return ValidateResponse(
        landing_page=landing_page,
        survey=survey,
        whatsapp_message=whatsapp,
        communities=communities,
        scorecard=scorecard,
        strategy=strategy,
        expected_outcomes=expected_outcomes,
        simulation=simulation,
        recommended_sequence=recommended_sequence,
    )


def _normalize_question_type(t: str) -> str:
    valid = {"multiple_choice", "scale", "open_text", "email", "yes_no"}
    t = t.lower().strip().replace(" ", "_").replace("-", "_")
    return t if t in valid else "open_text"


def _normalize_platform(p: str) -> str:
    valid = {"facebook", "discord", "nextdoor", "reddit", "linkedin", "whatsapp", "other"}
    p = p.lower().strip()
    return p if p in valid else "other"


def _build_validation_strategy(channels: list[str], scorecard: Scorecard) -> ValidationStrategy:
    methods = []
    if "landing_page" in channels:
        methods.append("Landing page")
    if "survey" in channels:
        methods.append("Survey")
    if "whatsapp" in channels:
        methods.append("Direct outreach")
    if "communities" in channels:
        methods.append("Community seeding")

    if "landing_page" in channels and "survey" in channels:
        typical_conversion = 0.05
    elif "landing_page" in channels:
        typical_conversion = 0.04
    else:
        typical_conversion = 0.03

    return ValidationStrategy(
        business_model="Demand validation",
        recommended_methods=methods,
        effort_estimate_hours=max(6, len(methods) * 4),
        timeline_weeks=max(1, len(methods)),
        typical_conversion_rate=typical_conversion,
        typical_cac=round(max(5.0, scorecard.price_tolerance_target * 0.8), 1),
        description="Run the highest-signal test first, then add qualification and outreach once response quality is clear.",
    )


def _build_expected_outcomes(channels: list[str], scorecard: Scorecard) -> dict:
    outcomes = {}
    if "landing_page" in channels:
        outcomes["landing_page"] = {
            "ctr": "10-15%",
            "conversion": "3-5%",
            "primary_goal": f"{scorecard.waitlist_target}+ signups",
        }
    if "survey" in channels:
        outcomes["survey"] = {
            "completion_rate": "60-75%",
            "qualified_demand": f"{scorecard.switch_pct_target}%+ positive switch intent",
            "primary_goal": f"{scorecard.survey_target}+ completed responses",
        }
    if "whatsapp" in channels:
        outcomes["whatsapp"] = {
            "reply_rate": "15-25%",
            "conversion": "20-30% of replies become qualified conversations",
            "primary_goal": "10+ replies from 50 messages",
        }
    if "communities" in channels:
        outcomes["communities"] = {
            "engagement_rate": "5-10%",
            "conversion": "3+ communities show positive traction",
            "primary_goal": "Identify repeatable acquisition channels",
        }
    return outcomes


def _build_simulation(channels: list[str], scorecard: Scorecard) -> dict:
    visitors = 1000 if "landing_page" in channels else 300
    signup_rate = 0.12 if "landing_page" in channels else 0.08
    signups = int(visitors * signup_rate)

    simulation = {
        "starting_audience": visitors,
        "expected_signups": signups,
        "expected_paid_conversions": max(scorecard.paid_signups_target, int(signups * 0.25)),
        "notes": [],
    }
    if "landing_page" in channels:
        simulation["notes"].append(f"If {visitors} visitors arrive, expect about {signups} signups.")
    if "survey" in channels:
        responses = max(scorecard.survey_target, int(signups * 0.5))
        simulation["expected_survey_responses"] = responses
        simulation["notes"].append(f"That should produce roughly {responses} completed surveys.")
    if "whatsapp" in channels or "communities" in channels:
        messages = 50
        replies = 10 if "whatsapp" in channels else 6
        simulation["outreach_messages"] = messages
        simulation["expected_replies"] = replies
        simulation["notes"].append(f"Sending {messages} targeted messages should yield around {replies} meaningful replies.")
    return simulation


def _build_recommended_sequence(channels: list[str]) -> list[str]:
    sequence = []
    if "landing_page" in channels:
        sequence.append("Step 1: Launch the landing page and measure visitor-to-signup conversion.")
    if "survey" in channels:
        sequence.append("Step 2: Send the survey to new signups and qualified interest leads.")
    if "whatsapp" in channels:
        sequence.append("Step 3: Run direct outreach with the best-performing hook from earlier tests.")
    if "communities" in channels:
        step_num = len(sequence) + 1
        sequence.append(f"Step {step_num}: Test distribution in communities and compare response quality by channel.")
    if not sequence:
        sequence.append("Step 1: Start with scorecard-based validation and benchmark whether stronger demand signals emerge.")
    return sequence
