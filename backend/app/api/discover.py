"""
POST /api/discover-insights
Scans Reddit + Google for market insights and pain points.
Pipeline: Data ingestion → Cleaning → Merging → Insight generation → Response
"""

import logging
from fastapi import APIRouter, Depends

from app.core.auth import optional_user
from app.schemas.models import (
    DiscoverRequest, DiscoverResponse, Insight, Evidence, SourceSummary,
)
from app.services.reddit_scraper import fetch_search_posts, extract_post_fields
from app.services.google_search import run_search_queries, build_discover_queries
from app.services.data_cleaner import (
    clean_reddit_posts, clean_search_results, merge_all_sources, build_source_summary,
)

logger = logging.getLogger(__name__)
router = APIRouter()
SERPER_QUERY_CAP = 5
POST_BUDGET = 80
SAMPLE_PER_GROUP = 5


@router.post("/api/discover-insights", response_model=DiscoverResponse)
async def discover_insights(
    req: DiscoverRequest,
    user: dict | None = Depends(optional_user),
):
    """Discover market insights from Reddit and Google search."""
    decomp = req.decomposition.model_dump() if hasattr(req.decomposition, 'model_dump') else req.decomposition
    loc = decomp.get("location", {})
    city = loc.get("city", "")
    state = loc.get("state", "")
    business_type = decomp.get("business_type", "")

    # Fetch Reddit posts
    reddit_posts = []
    search_queries_list = decomp.get("search_queries", [])
    reddit_search_q = search_queries_list[0] if search_queries_list else f"{business_type} {city} {state}".strip()

    if reddit_search_q:
        try:
            raw_search_posts = await fetch_search_posts(reddit_search_q, limit=60)
            reddit_posts = [extract_post_fields(p) for p in raw_search_posts]
        except Exception as e:
            logger.warning(f"Reddit search failed: {e}")

    # Fetch Google search results
    search_queries = decomp.get("search_queries", [])
    if not search_queries:
        search_queries = build_discover_queries(decomp)
    search_queries = search_queries[:SERPER_QUERY_CAP]
    location_str = f"{city}, {state}" if city and state else None
    raw_search = await run_search_queries(search_queries, location=location_str, num_per_query=10)

    # Clean and merge data
    cleaned_reddit = clean_reddit_posts(reddit_posts)
    cleaned_search = clean_search_results(raw_search, query_type="discover")
    merged = merge_all_sources(cleaned_reddit, cleaned_search, max_items=200)
    sources = build_source_summary(merged)

    # Generate insights from data
    merged_sampled = _sample_posts(merged, budget=POST_BUDGET, per_group=SAMPLE_PER_GROUP)
    fallback = _fallback_insights(merged_sampled)

    return _post_process(fallback, sources)


def _post_process(scored_data: dict, sources: list[dict]) -> DiscoverResponse:
    """Format insights into response model."""
    raw_insights = scored_data.get("insights", [])

    insights = []
    for i, raw in enumerate(raw_insights[:12]):
        pain_score = raw.get("pain_score", raw.get("score", 0))
        if isinstance(pain_score, (int, float)) and pain_score > 10:
            pain_score = pain_score / 10.0

        evidence_list = []
        for ev in raw.get("evidence", [])[:2]:
            evidence_list.append(Evidence(
                quote=ev.get("quote", ""),
                source=ev.get("source", ""),
                score=ev.get("score", 0),
                upvotes=ev.get("upvotes"),
                date=ev.get("date"),
            ))

        freq = raw.get("frequency", raw.get("frequency_score", 0))
        mention_count = int(freq) if isinstance(freq, (int, float)) else 0

        insight = Insight(
            id=f"ins_{i+1:03d}",
            type=_normalize_type(raw.get("type", "pain_point")),
            title=raw.get("title", ""),
            score=round(min(10.0, max(0.0, float(pain_score))), 1),
            frequency_score=_clamp(raw.get("frequency_score", 0)),
            intensity_score=_clamp(raw.get("intensity_score", 0)),
            willingness_to_pay_score=_clamp(raw.get("willingness_to_pay_score", 0)),
            mention_count=mention_count,
            evidence=evidence_list[:3],
            source_platforms=raw.get("source_platforms", []),
            audience_estimate=raw.get("audience_estimate", ""),
        )
        insights.append(insight)

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
