"""
POST /api/discover-insights
Scans Reddit + Google for market insights and pain points.
Pipeline: Data ingestion → Cleaning → Merging → Insight generation → Response
"""

import logging
import json
import re
from collections import Counter
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import optional_user
from app.services.llm_client import call_llm
from app.schemas.models import (
    DiscoverRequest, DiscoverResponse, Insight, Evidence, SourceSummary, DiscoverSummary,
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
SERPER_QUERY_CAP = 2        # Lower fan-out for faster discovery
POST_BUDGET = 20            # Smaller evidence bundle for faster LLM extraction
SAMPLE_PER_GROUP = 5


@router.post("/api/discover-insights", response_model=DiscoverResponse)
async def discover_insights(
    req: DiscoverRequest,
    user: dict | None = Depends(optional_user),
):
    """Discover market insights from Reddit and Google search."""
    # Prefer provided decomposition so downstream tabs can reuse shared context.
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
            raw_search_posts = await fetch_search_posts(reddit_search_q, limit=25)
            return [extract_post_fields(p) for p in raw_search_posts]
        except Exception as e:
            logger.warning(f"Reddit search failed: {e}")
            return []

    reddit_posts, raw_search = await asyncio.gather(
        fetch_reddit(),
        run_search_queries(search_queries, location=location_str, num_per_query=5)
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

    response = _post_process(llm_insights, sources, merged, city, state)

    # ✅ STORE IN DATABASE CACHE for future similar queries
    await cache_discover(business_type, city, state, response)

    return response


def _post_process(scored_data: dict, sources: list[dict], merged_posts: list[dict], city: str, state: str) -> DiscoverResponse:
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
    summary = _build_discover_summary(raw_insights, insights, merged_posts, city, state)

    return DiscoverResponse(sources=source_models, insights=insights, summary=summary)


def _build_discover_summary(
    raw_insights: list[dict],
    insights: list[Insight],
    merged_posts: list[dict],
    city: str,
    state: str,
) -> DiscoverSummary:
    if not insights:
        return DiscoverSummary(
            demand_strength=0.0,
            signal_density="low",
            trend_direction="stable",
            trend_label="Stable",
            top_regions=[label for label in [city, state] if label][:2],
            mixed_signals=[],
            summary="Limited demand evidence available yet.",
        )

    avg_score = sum(i.score for i in insights) / len(insights)
    avg_mentions = sum(max(i.mention_count, 1) for i in insights) / len(insights)
    avg_intensity = sum(i.intensity_score for i in insights) / len(insights)
    avg_wtp = sum(i.willingness_to_pay_score for i in insights) / len(insights)
    platform_diversity = len({platform for i in insights for platform in i.source_platforms})

    demand_strength = round(min(10.0, (avg_score * 0.6) + (avg_intensity * 0.25) + (avg_wtp * 0.15)), 1)

    density_score = avg_mentions + (platform_diversity * 1.2)
    if density_score >= 10:
        signal_density = "high"
    elif density_score >= 6:
        signal_density = "medium"
    else:
        signal_density = "low"

    trend_direction, trend_label = _calculate_trend_direction(raw_insights, merged_posts)
    top_regions = _extract_top_regions(merged_posts, city, state)
    mixed_signals = _detect_mixed_signals(insights, raw_insights)

    summary = (
        f"Demand strength {demand_strength}/10 with {signal_density} signal density. "
        f"Trend is {trend_label.lower()}."
    )
    if mixed_signals:
        summary += f" Mixed signals detected: {mixed_signals[0]}"

    return DiscoverSummary(
        demand_strength=demand_strength,
        signal_density=signal_density,
        trend_direction=trend_direction,
        trend_label=trend_label,
        top_regions=top_regions,
        mixed_signals=mixed_signals,
        summary=summary,
    )


def _calculate_trend_direction(raw_insights: list[dict], merged_posts: list[dict]) -> tuple[str, str]:
    urgency_values = []
    for raw in raw_insights:
        try:
            urgency_values.append(float(raw.get("urgency", 0)))
        except (TypeError, ValueError):
            continue

    recent_posts = 0
    dated_posts = 0
    now = datetime.now(timezone.utc)
    for post in merged_posts:
        parsed = _parse_date(post.get("created_date"))
        if not parsed:
            continue
        dated_posts += 1
        age_days = (now - parsed).days
        if age_days <= 180:
            recent_posts += 1

    urgency_avg = sum(urgency_values) / len(urgency_values) if urgency_values else 0
    recent_ratio = (recent_posts / dated_posts) if dated_posts else 0

    if urgency_avg >= 7 or recent_ratio >= 0.55:
        return "growing", "Growing (last 6 months)"
    if urgency_avg <= 3 and recent_ratio < 0.2:
        return "declining", "Cooling"
    return "stable", "Stable"


def _parse_date(value: str | None):
    if not value:
        return None
    for candidate in (
        str(value).replace("Z", "+00:00"),
        f"{value}T00:00:00+00:00" if isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) else None,
    ):
        if not candidate:
            continue
        try:
            parsed = datetime.fromisoformat(candidate)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc)
        except ValueError:
            continue
    return None


def _extract_top_regions(merged_posts: list[dict], city: str, state: str) -> list[str]:
    region_patterns = {
        "Austin": r"\baustin\b",
        "Dallas": r"\bdallas\b",
        "Plano": r"\bplano\b",
        "Houston": r"\bhouston\b",
        "San Francisco": r"\bsan francisco\b|\bsf\b",
        "New York": r"\bnew york\b|\bnyc\b",
        "Los Angeles": r"\blos angeles\b|\bla\b",
        "Chicago": r"\bchicago\b",
        "Seattle": r"\bseattle\b",
    }

    counts: Counter[str] = Counter()
    for post in merged_posts:
        text = " ".join(
            str(post.get(field, "") or "")
            for field in ("title", "body", "snippet", "query")
        ).lower()
        for region, pattern in region_patterns.items():
            if re.search(pattern, text):
                counts[region] += 1

    if city:
        counts[city] += 2
    if state and state not in counts:
        counts[state] += 1

    regions = [region for region, _ in counts.most_common(3)]
    if not regions:
        regions = [label for label in [city, state] if label]
    return regions[:3]


def _detect_mixed_signals(insights: list[Insight], raw_insights: list[dict]) -> list[str]:
    if not insights:
        return []

    avg_intensity = sum(i.intensity_score for i in insights) / len(insights)
    avg_wtp = sum(i.willingness_to_pay_score for i in insights) / len(insights)
    trend_count = sum(1 for i in insights if i.type == "trend")
    pain_count = sum(1 for i in insights if i.type == "pain_point")
    gap_count = sum(1 for i in insights if i.type == "market_gap")

    mixed_signals: list[str] = []
    if avg_intensity >= 6.5 and avg_wtp <= 4.5:
        mixed_signals.append("High demand intensity but weak willingness to pay")
    if trend_count > 0 and pain_count == 0:
        mixed_signals.append("Growing discussion but limited hard pain evidence")
    if gap_count > 0 and avg_wtp < 5:
        mixed_signals.append("Clear market gaps but monetization is still uncertain")

    low_confidence = sum(1 for raw in raw_insights if str(raw.get("confidence", "medium")).lower() == "low")
    if low_confidence >= max(1, len(raw_insights) // 3):
        mixed_signals.append("Some signals are directional rather than high-confidence proof")

    return mixed_signals[:3]


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
            max_tokens=1200,  # Keep response compact for lower latency
            json_mode=True,
            preferred_provider="groq",
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
