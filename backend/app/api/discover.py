"""
POST /api/discover-insights
Scans Reddit + Google for market insights and pain points.
Pipeline: Data ingestion → Cleaning → Merging → Insight generation → Response
"""

import logging
import json
from fastapi import APIRouter, Depends

from app.core.auth import optional_user
from app.services.llm_client import call_llm
from app.schemas.models import (
    DiscoverRequest, DiscoverResponse, Insight, Evidence, SourceSummary,
)
from app.services.reddit_scraper import fetch_search_posts, extract_post_fields
from app.services.google_search import run_search_queries, build_discover_queries
from app.services.data_cleaner import (
    clean_reddit_posts, clean_search_results, merge_all_sources, build_source_summary,
)
from app.services.cache_service import get_cached_discover, cache_discover
from app.services.ranking_service import calculate_composite_score
from app.prompts.templates import discover_extract_signals_system, discover_extract_signals_user

logger = logging.getLogger(__name__)
router = APIRouter()
SERPER_QUERY_CAP = 3        # Reduced from 5 for faster discovery
POST_BUDGET = 40            # Reduced from 80 for faster Reddit scraping
SAMPLE_PER_GROUP = 5


@router.post("/api/discover-insights", response_model=DiscoverResponse)
async def discover_insights(
    req: DiscoverRequest,
    user: dict | None = Depends(optional_user),
):
    """Discover market insights from Reddit and Google search."""
    # Step 1: Call decompose internally to get business structure
    from app.api.decompose import decompose_idea
    from app.schemas.models import DecomposeRequest

    decompose_req = DecomposeRequest(idea=req.idea)
    decomp_response = await decompose_idea(decompose_req, user=user)
    decomp = decomp_response.model_dump() if hasattr(decomp_response, 'model_dump') else decomp_response

    loc = decomp.get("location", {})
    city = loc.get("city", "")
    state = loc.get("state", "")
    business_type = decomp.get("business_type", "")

    # ✅ CHECK DATABASE CACHE FIRST (for similar queries)
    cached = await get_cached_discover(business_type, city, state)
    if cached:
        logger.info(f"✅ Cache hit: discover for {business_type} in {city}, {state}")
        return cached

    # ✅ PARALLEL: Fetch Reddit posts and Google search in parallel
    import asyncio

    reddit_posts = []
    search_queries_list = decomp.get("search_queries", [])
    reddit_search_q = search_queries_list[0] if search_queries_list else f"{business_type} {city} {state}".strip()

    search_queries = decomp.get("search_queries", [])
    if not search_queries:
        search_queries = build_discover_queries(decomp)
    search_queries = search_queries[:SERPER_QUERY_CAP]
    location_str = f"{city}, {state}" if city and state else None

    # Run both API calls in parallel
    async def fetch_reddit():
        if not reddit_search_q:
            return []
        try:
            raw_search_posts = await fetch_search_posts(reddit_search_q, limit=60)
            return [extract_post_fields(p) for p in raw_search_posts]
        except Exception as e:
            logger.warning(f"Reddit search failed: {e}")
            return []

    reddit_posts, raw_search = await asyncio.gather(
        fetch_reddit(),
        run_search_queries(search_queries, location=location_str, num_per_query=5)  # Reduced for speed
    )

    # Clean and merge data
    cleaned_reddit = clean_reddit_posts(reddit_posts)
    cleaned_search = clean_search_results(raw_search, query_type="discover")
    merged = merge_all_sources(cleaned_reddit, cleaned_search, max_items=200)
    sources = build_source_summary(merged)

    # ✅ INTELLIGENT INSIGHT EXTRACTION (LLM with all 4 signals)
    merged_sampled = _sample_posts(merged, budget=POST_BUDGET, per_group=SAMPLE_PER_GROUP)

    # Call LLM to extract insights with Intensity, Willingness-to-Pay, Market Size, Urgency
    llm_insights = await _extract_insights_with_signals(
        merged_sampled, business_type, city, state
    )

    response = _post_process(llm_insights, sources)

    # ✅ STORE IN DATABASE CACHE for future similar queries
    await cache_discover(business_type, city, state, response)

    return response


def _post_process(scored_data: dict, sources: list[dict]) -> DiscoverResponse:
    """Format insights into response model with LLM-extracted signal values."""
    raw_insights = scored_data.get("insights", [])

    insights = []
    for i, raw in enumerate(raw_insights[:12]):
        # Extract all 4 signals from LLM (now intelligent, not hardcoded)
        mention_count = raw.get("mention_count", 0)

        # Build evidence list with supporting quotes from analysis
        evidence_list = []
        customer_quote = raw.get("customer_quote", "")
        if customer_quote:
            source_platforms = raw.get("source_platforms", [])
            source = source_platforms[0] if source_platforms else "research"
            evidence_list.append(Evidence(
                quote=customer_quote,
                source=source,
                source_url="",
                score=0,
                upvotes=None,
                date=None,
            ))

        explanation = raw.get("explanation", "")
        if explanation and len(evidence_list) < 3:
            evidence_list.append(Evidence(
                quote=explanation,
                source="analysis",
                source_url="",
                score=0,
                upvotes=None,
                date=None,
            ))

        # Create insight object with LLM-extracted signal values
        insight = Insight(
            id=f"ins_{i+1:03d}",
            type=_normalize_type(raw.get("type", "pain_point")),
            title=raw.get("title", ""),
            score=0.0,  # Will be set by composite scoring below
            # ✅ Use LLM-extracted signal values (not hardcoded defaults)
            frequency_score=_clamp(raw.get("frequency_score", raw.get("mention_count", 0) / 3)),
            intensity_score=_clamp(raw.get("intensity", 5)),  # LLM extracts as "intensity"
            willingness_to_pay_score=_clamp(raw.get("willingness_to_pay", 5)),  # LLM extracts as "willingness_to_pay"
            mention_count=mention_count,
            evidence=evidence_list[:3],
            source_platforms=raw.get("source_platforms", []),
            audience_estimate=raw.get("market_size_estimate", ""),  # Market size described as text
        )

        # ✅ Enrich raw data with LLM values for composite scoring
        raw["frequency_score"] = raw.get("mention_count", 0) / 3  # Derive from mention count
        raw["intensity_score"] = raw.get("intensity", 5)
        raw["willingness_to_pay_score"] = raw.get("willingness_to_pay", 5)
        raw["market_size"] = raw.get("market_size", 5)  # Direct from LLM
        raw["urgency"] = raw.get("urgency", 5)  # Direct from LLM

        # ✅ Calculate composite score with LLM-informed signals
        insight.score = calculate_composite_score(raw)

        insights.append(insight)

    # ✅ Sort by composite score (descending = best insights first)
    insights.sort(key=lambda x: x.score, reverse=True)

    source_models = [SourceSummary(**s) for s in sources]

    return DiscoverResponse(sources=source_models, insights=insights)


def _sample_posts(posts: list[dict], budget: int, per_group: int) -> list[dict]:
    """Stratified sample to maintain diversity."""
    buckets = {}
    for p in posts:
        key = p.get("subreddit") or p.get("query_type") or "misc"
        buckets.setdefault(key, []).append(p)

    sampled = []
    for key, items in buckets.items():
        sampled.extend(items[:per_group])

    def score(p):
        return p.get("score", 0) or p.get("rating", 0) or 0

    sampled.sort(key=score, reverse=True)
    return sampled[:budget]


def _fallback_insights(posts: list[dict]) -> dict:
    """Generate insights from posts using keyword analysis."""
    types = ["pain_point", "unmet_want", "market_gap", "opportunity"]

    if not posts:
        return {"insights": [{
            "id": "fallback_1",
            "type": "market_gap",
            "title": "Limited local market discussion",
            "score": 6,
            "frequency_score": 5,
            "intensity_score": 5,
            "willingness_to_pay_score": 4,
            "mention_count": 0,
            "evidence": [{"quote": "Low volume suggests market opportunity", "source": "analysis", "score": 0}],
            "source_platforms": ["research"],
            "audience_estimate": "",
        }]}

    texts = []
    for p in posts:
        texts.append(p.get("title", ""))
        texts.append(p.get("body", p.get("snippet", "")))
    full = " ".join(texts).lower()

    keyword_groups = {
        "pricing": ["price", "cost", "expensive", "overpriced", "cheap", "affordable"],
        "wait times": ["wait", "slow", "fast", "line", "queue", "delay"],
        "quality": ["quality", "taste", "fresh", "health", "organic"],
        "location": ["location", "distance", "far", "convenient", "access"],
        "service": ["service", "staff", "experience", "rude", "friendly"],
    }

    insights = []
    for group_name, terms in keyword_groups.items():
        found_terms = [t for t in terms if t in full]
        if found_terms:
            mention_count = sum(1 for p in posts
                              if any(t in (p.get("title", "") + p.get("body", p.get("snippet", ""))).lower()
                                    for t in found_terms))

            insights.append({
                "id": f"fallback_{len(insights)+1}",
                "type": types[len(insights) % len(types)],
                "title": f"Customer concerns: {group_name}",
                "score": 5 + (min(len(found_terms), 3) * 0.5),
                "frequency_score": min(6, 3 + len(found_terms)),
                "intensity_score": 4,
                "willingness_to_pay_score": 3,
                "mention_count": mention_count,
                "evidence": [{"quote": f"Keywords: {', '.join(found_terms)}", "source": "analysis", "score": 0}],
                "source_platforms": ["research"],
                "audience_estimate": "",
            })

    if not insights:
        insights = [{
            "id": "fallback_1",
            "type": "market_gap",
            "title": "Market research opportunity",
            "score": 5,
            "frequency_score": 4,
            "intensity_score": 4,
            "willingness_to_pay_score": 3,
            "mention_count": len(posts),
            "evidence": [{"quote": f"Analyzed {len(posts)} sources", "source": "analysis", "score": 0}],
            "source_platforms": ["research"],
            "audience_estimate": "",
        }]

    return {"insights": insights[:5]}


async def _extract_insights_with_signals(
    posts: list[dict], business_type: str, city: str, state: str
) -> dict:
    """
    ✅ NEW: LLM-powered insight extraction with intelligent signal detection.
    Extracts: Intensity, Willingness-to-Pay, Market Size, Urgency from actual data.
    """
    if not posts:
        logger.warning("[DISCOVER] No posts to analyze, using fallback")
        return {"insights": []}

    try:
        # Call LLM to extract insights with all 4 signals
        system_prompt = discover_extract_signals_system(business_type, city, state)
        user_prompt = discover_extract_signals_user(posts, business_type, city, state)

        logger.info(f"[DISCOVER] Extracting insights with LLM ({len(posts)} posts)")

        response = await call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.4,  # Moderate - balance consistency with insight discovery
            max_tokens=2000,  # Room for 8-12 detailed insights
            json_mode=True,
            preferred_provider="gemini",
        )

        # Parse LLM response
        try:
            insights_data = json.loads(response) if isinstance(response, str) else response
            insights = insights_data.get("insights", [])

            if not insights:
                logger.warning("[DISCOVER] LLM returned empty insights, using fallback")
                return _fallback_insights(posts)

            logger.info(f"[DISCOVER] LLM extracted {len(insights)} insights")
            return {"insights": insights}

        except json.JSONDecodeError as e:
            logger.error(f"[DISCOVER] Failed to parse LLM response: {e}")
            return _fallback_insights(posts)

    except Exception as e:
        logger.error(f"[DISCOVER] LLM extraction failed: {e}. Falling back to keyword analysis.")
        # Graceful fallback to keyword-based analysis
        return _fallback_insights(posts)


def _normalize_type(t: str) -> str:
    """Normalize insight type."""
    valid = {"pain_point", "unmet_want", "market_gap", "trend"}
    t = t.lower().strip().replace(" ", "_")
    return t if t in valid else "pain_point"


def _clamp(v, lo=0.0, hi=10.0) -> float:
    """Clamp value to range."""
    try:
        v = float(v)
        if v > hi:
            v = v / 10.0
        return round(min(hi, max(lo, v)), 1)
    except (TypeError, ValueError):
        return 0.0
