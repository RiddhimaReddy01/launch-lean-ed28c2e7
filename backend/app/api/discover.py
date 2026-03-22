"""
POST /api/discover-insights
Scans Reddit + Google → cleans → merges → LLM categorization → scoring → response.
This is the data-heaviest endpoint in the pipeline.
"""

import json
import logging
from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import optional_user
from app.schemas.models import (
    DiscoverRequest, DiscoverResponse, Insight, Evidence, SourceSummary,
)
from app.services.llm_client import call_llm, AllProvidersExhaustedError
from app.services.reddit_scraper import fetch_all_subreddits, fetch_search_posts, extract_post_fields
from app.services.google_search import run_search_queries, build_discover_queries
from app.services.data_cleaner import (
    clean_reddit_posts, clean_search_results, merge_all_sources, build_source_summary,
)
from app.prompts.templates import (
    discover_categorize_system, discover_categorize_user,
    discover_score_system, discover_score_user,
)

logger = logging.getLogger(__name__)
router = APIRouter()
POST_BUDGET = 80  # total posts passed to LLM
SAMPLE_PER_GROUP = 5  # max per subreddit/query group
SERPER_QUERY_CAP = 5


@router.post("/api/discover-insights", response_model=DiscoverResponse)
async def discover_insights(
    req: DiscoverRequest,
    user: dict | None = Depends(optional_user),
):
    # Convert Pydantic model to dict for uniform access
    decomp = req.decomposition.model_dump() if hasattr(req.decomposition, 'model_dump') else req.decomposition
    loc = decomp.get("location", {})
    city = loc.get("city", "")
    state = loc.get("state", "")
    business_type = decomp.get("business_type", "")

    # ═══ STAGE 1: DATA INGESTION ═══
    logger.info(f"Discover: ingesting data for '{business_type}' in {city}, {state}")

    # 1a. Reddit posts - use first search query for targeted results
    subreddits = decomp.get("subreddits", [])
    reddit_posts = []

    # Use first search query (most relevant from decomposition)
    search_queries_list = decomp.get("search_queries", [])
    reddit_search_q = ""
    if search_queries_list:
        reddit_search_q = search_queries_list[0]  # Use most relevant query
    else:
        # Fallback: build simple search query
        reddit_search_q = f"{business_type} {city} {state}".strip()

    # Fetch Reddit posts
    if reddit_search_q:
        try:
            raw_search_posts = await fetch_search_posts(reddit_search_q, limit=60)
            reddit_posts = [extract_post_fields(p) for p in raw_search_posts]
        except Exception as e:
            logger.warning(f"Reddit search failed for '{reddit_search_q}': {e}")

    # 1b. Google search results via Serper
    search_queries = decomp.get("search_queries", [])
    if not search_queries:
        search_queries = build_discover_queries(decomp)
    search_queries = search_queries[:SERPER_QUERY_CAP]
    location_str = f"{city}, {state}" if city and state else None
    raw_search = await run_search_queries(search_queries, location=location_str, num_per_query=10)

    # ═══ STAGE 2: DATA CLEANING ═══
    cleaned_reddit = clean_reddit_posts(reddit_posts)
    cleaned_search = clean_search_results(raw_search, query_type="discover")

    # ═══ STAGE 3: DATA TRANSFORMATION ═══
    merged = merge_all_sources(cleaned_reddit, cleaned_search, max_items=200)
    sources = build_source_summary(merged)

    if len(merged) < 3:
        logger.warning("Very few posts after cleaning, results may be thin")

    # ═══ STAGE 4: LLM LOGIC ═══
    # Rerank/sample before LLM
    merged_sampled = _sample_posts(merged, budget=POST_BUDGET, per_group=SAMPLE_PER_GROUP)

    try:
        if len(merged_sampled) <= 60:
            # Single-pass: categorize + score in one go
            cat_system = discover_categorize_system(business_type, city, state)
            cat_user = discover_categorize_user(merged_sampled, len(merged_sampled), include_score=True)
            scored = await call_llm(
                system_prompt=cat_system,
                user_prompt=cat_user,
                temperature=0.25,
                max_tokens=1400,
                json_mode=True,
            )
        else:
            # Two-pass for larger sets
            cat_system = discover_categorize_system(business_type, city, state)
            cat_user = discover_categorize_user(merged_sampled, len(merged_sampled))

            categorized = await call_llm(
                system_prompt=cat_system,
                user_prompt=cat_user,
                temperature=0.25,
                max_tokens=1600,
                json_mode=True,
            )

            insights_raw = categorized.get("insights", categorized if isinstance(categorized, list) else [])
            score_system = discover_score_system()
            score_user = discover_score_user(json.dumps({"insights": insights_raw[:12]}, indent=2))

            scored = await call_llm(
                system_prompt=score_system,
                user_prompt=score_user,
                temperature=0.2,
                max_tokens=900,
                json_mode=True,
            )

    except AllProvidersExhaustedError:
        # Heuristic fallback
        fallback = _fallback_insights(merged_sampled)
        return _post_process(fallback, sources, note="fallback")

    # ═══ STAGE 5: POST-PROCESSING ═══
    # Check if LLM returned empty insights; use fallback if so
    if not scored.get("insights"):
        logger.warning("LLM returned empty insights, using fallback")
        fallback = _fallback_insights(merged_sampled)
        return _post_process(fallback, sources, note="fallback_empty")

    return _post_process(scored, sources)


def _post_process(scored_data: dict, sources: list[dict], note: str | None = None) -> DiscoverResponse:
    """Validate, normalize, and format the final response."""

    raw_insights = scored_data.get("insights", scored_data if isinstance(scored_data, list) else [])

    insights = []
    for i, raw in enumerate(raw_insights[:12]):  # Cap at 12
        # Normalize scores to 0-10
        pain_score = raw.get("pain_score", raw.get("score", 0))
        if isinstance(pain_score, (int, float)) and pain_score > 10:
            pain_score = pain_score / 10.0  # Normalize if LLM gave 0-100

        # Build evidence list
        evidence_list = []
        for ev in raw.get("evidence", [])[:2]:
            evidence_list.append(Evidence(
                quote=ev.get("quote", ""),
                source=ev.get("source", ""),
                score=ev.get("score", 0),
                upvotes=ev.get("upvotes"),
                date=ev.get("date"),
            ))

        # Calculate mention count from frequency
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

    # Sort by score descending
    insights.sort(key=lambda x: x.score, reverse=True)

    # Build source summaries
    source_models = [SourceSummary(**s) for s in sources]

    resp = DiscoverResponse(sources=source_models, insights=insights)
    if note:
        # attach note via model serialization
        resp_dict = resp.model_dump()
        resp_dict["note"] = note
        return DiscoverResponse(**resp_dict)
    return resp


def _sample_posts(posts: list[dict], budget: int, per_group: int) -> list[dict]:
    """Stratified sample across subreddit/query_type to keep diversity."""
    buckets = {}
    for p in posts:
        key = p.get("subreddit") or p.get("query_type") or "misc"
        buckets.setdefault(key, []).append(p)
    sampled = []
    for key, items in buckets.items():
        sampled.extend(items[:per_group])
    # Trim to budget by score if available
    def score(p): return p.get("score", 0) or p.get("rating", 0) or 0
    sampled.sort(key=score, reverse=True)
    return sampled[:budget]


def _fallback_insights(posts: list[dict]) -> dict:
    """Heuristic insights when LLM unavailable."""
    types = ["pain_point", "unmet_want", "market_gap", "opportunity"]

    # If no posts, return generic insights based on business opportunity
    if not posts:
        return {"insights": [
            {
                "id": "fallback_1",
                "type": "market_gap",
                "title": "Limited local reviews and discussion",
                "score": 6,
                "frequency_score": 5,
                "intensity_score": 5,
                "willingness_to_pay_score": 4,
                "mention_count": 0,
                "evidence": [{"quote": "Low search volume indicates potential market gap", "source": "analysis", "score": 0}],
                "source_platforms": ["reddit", "search"],
                "audience_estimate": "",
            }
        ]}

    # Extract keywords from posts
    texts = []
    for p in posts:
        texts.append(p.get("title", ""))
        texts.append(p.get("body", p.get("snippet", "")))
    full = " ".join(texts).lower()

    # Extended keyword list for better coverage
    keyword_groups = {
        "price/cost": ["price", "cost", "expensive", "overpriced", "cheap", "affordable"],
        "wait/speed": ["wait", "slow", "fast", "line", "queue", "delay"],
        "quality": ["quality", "taste", "fresh", "health", "organic"],
        "location": ["location", "distance", "far", "convenient", "access"],
        "customer service": ["service", "staff", "experience", "rude", "friendly"],
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
                "evidence": [{"quote": f"Found keywords: {', '.join(found_terms)}", "source": "analysis", "score": 0}],
                "source_platforms": ["reddit", "search"],
                "audience_estimate": "",
            })

    # Always return at least 2 insights
    if not insights:
        insights = [
            {
                "id": "fallback_1",
                "type": "market_gap",
                "title": "Emerging market opportunity",
                "score": 5,
                "frequency_score": 4,
                "intensity_score": 4,
                "willingness_to_pay_score": 3,
                "mention_count": len(posts),
                "evidence": [{"quote": f"Analysis of {len(posts)} sources", "source": "analysis", "score": 0}],
                "source_platforms": ["reddit", "search"],
                "audience_estimate": "",
            }
        ]

    return {"insights": insights[:5]}

def _normalize_type(t: str) -> str:
    valid = {"pain_point", "unmet_want", "market_gap", "trend"}
    t = t.lower().strip().replace(" ", "_")
    return t if t in valid else "pain_point"


def _clamp(v, lo=0.0, hi=10.0) -> float:
    try:
        v = float(v)
        if v > hi:
            v = v / 10.0  # Normalize 0-100 to 0-10
        return round(min(hi, max(lo, v)), 1)
    except (TypeError, ValueError):
        return 0.0
