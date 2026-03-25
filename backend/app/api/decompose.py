"""
POST /api/decompose-idea
Converts raw idea string → structured searchable components.
Pipeline: Input validation → LLM extraction → Post-processing → Response
"""

import asyncio
import logging
from fastapi import APIRouter, Depends, HTTPException
import time

from app.core.auth import optional_user
from app.schemas.models import DecomposeRequest, DecomposeResponse, Location
from app.services.llm_client import call_llm, AllProvidersExhaustedError
from app.services.cache_service import get_cached_decompose, cache_decompose
from app.prompts.templates import (
    decompose_system, decompose_user,
    decompose_stage1_system, decompose_stage1_user,
    decompose_stage2_system, decompose_stage2_user,
)

logger = logging.getLogger(__name__)
router = APIRouter()
CACHE_TTL_SECONDS = 900  # 15 minutes


@router.post("/api/decompose-idea", response_model=DecomposeResponse)
async def decompose_idea(
    req: DecomposeRequest,
    user: dict | None = Depends(optional_user),
):
    logger.info(f"🔵 decompose_idea called with: {req.idea}")

    idea = _preclean(req.idea)
    logger.info(f"🟢 Idea cleaned: {idea}")

    # Input validation
    if len(idea.split()) < 3:
        raise HTTPException(status_code=400, detail="Idea must be at least 3 words")

    # ✅ Check in-memory cache first (fastest)
    cached = await _cache_get(idea)
    if cached:
        logger.info(f"✅ In-memory cache hit")
        return cached

    # ✅ Check database cache second (for persistence across restarts)
    db_cached = await get_cached_decompose(idea)
    if db_cached:
        logger.info(f"✅ Database cache hit")
        await _cache_set(idea, db_cached)  # Repopulate in-memory
        return db_cached

    # ── STAGE 1: Fast extraction (business_type + location) ──
    logger.info("🔵 Stage 1: Extracting business type and location...")
    try:
        stage1_raw = await call_llm(
            system_prompt=decompose_stage1_system(),
            user_prompt=decompose_stage1_user(idea),
            temperature=0.05,
            max_tokens=150,
            json_mode=True,
        )
        business_type = stage1_raw.get("business_type", "")
        location_raw = stage1_raw.get("location", {})
        stage1_location = Location(
            city=location_raw.get("city", ""),
            state=_normalize_state(location_raw.get("state", "")),
        )
        logger.info(f"🟢 Stage 1 done: {business_type} in {stage1_location.city}, {stage1_location.state}")
    except Exception as e:
        logger.warning(f"Stage 1 failed ({type(e).__name__}), fallback extraction")
        business_type = idea[:80]
        stage1_location = Location()

    # ── STAGE 2: Detailed extraction (customers, pricing, queries) ──
    logger.info("🔵 Stage 2: Extracting detailed components...")
    vertical = _infer_vertical(business_type or idea)
    defaults = _default_domains_for_vertical(vertical)

    try:
        stage2_raw = await call_llm(
            system_prompt=decompose_stage2_system(),
            user_prompt=decompose_stage2_user(
                idea=idea,
                business_type=business_type,
                city=stage1_location.city,
                state=stage1_location.state,
                vertical=vertical,
                domain_suggestions=defaults,
            ),
            temperature=0.05,
            max_tokens=500,
            json_mode=True,
        )
        logger.info(f"🟢 Stage 2 done: Got target_customers, price_tier, source_domains, search_queries")
    except Exception as e:
        logger.warning(f"Stage 2 failed ({type(e).__name__}), using defaults")
        stage2_raw = {}

    if not isinstance(stage2_raw, dict):
        logger.warning(f"Stage 2 returned {type(stage2_raw).__name__}, using defaults")
        stage2_raw = {}

    # ── Combine and post-process ──
    combined = {
        "business_type": business_type,
        "location": {
            "city": stage1_location.city,
            "state": stage1_location.state,
        },
        **stage2_raw,
    }

    try:
        resp = _post_process(combined, defaults)
    except Exception as e:
        logger.warning(f"Post-process failed ({type(e).__name__}), using fallback")
        resp = _fallback_decompose(idea, vertical, defaults)

    # ✅ Store in both caches: in-memory (fast) + database (persistent)
    await _cache_set(idea, resp)
    await cache_decompose(idea, resp)

    return resp


def _post_process(raw: dict, defaults: list[str]) -> DecomposeResponse:
    """Validate and normalize LLM response."""

    default_domains = [
        "yelp.com", "google.com/maps", "trustpilot.com", "g2.com", "capterra.com",
        "producthunt.com", "news.ycombinator.com", "stackoverflow.com",
        "craigslist.org", "meetup.com", "eventbrite.com", "tripadvisor.com",
        "city-data.com/forum", "amazon.com",
    ]

    # Parse location
    loc_raw = raw.get("location", {})
    if isinstance(loc_raw, str):
        loc_raw = {"city": loc_raw, "state": "", "county": "", "metro": ""}
    location = Location(
        city=loc_raw.get("city", ""),
        state=_normalize_state(loc_raw.get("state", "")),
        county=loc_raw.get("county", ""),
        metro=loc_raw.get("metro", ""),
    )

    # Ensure subreddits has 4-8 entries
    subreddits = raw.get("subreddits", [])
    if isinstance(subreddits, str):
        subreddits = [s.strip() for s in subreddits.split(",") if s.strip()]
    elif not isinstance(subreddits, list):
        subreddits = []
    # Strip r/ prefix if present
    subreddits = [s.replace("r/", "").strip() for s in subreddits if isinstance(s, str)]
    # Pad with defaults if too few
    if len(subreddits) < 4 and location.city:
        defaults = [location.city.lower(), "smallbusiness", "Entrepreneur", "startups"]
        for d in defaults:
            if d not in subreddits and len(subreddits) < 4:
                subreddits.append(d)

    # Ensure search_queries has 5-8 entries
    queries = raw.get("search_queries", [])
    if isinstance(queries, str):
        queries = [queries] if queries.strip() else []
    elif not isinstance(queries, list):
        queries = []
    # Filter to strings only
    queries = [q for q in queries if isinstance(q, str) and q.strip()]

    source_domains = raw.get("source_domains", [])
    if isinstance(source_domains, str):
        source_domains = [d.strip() for d in source_domains.split(",") if d.strip()]
    elif not isinstance(source_domains, list):
        source_domains = []
    # Filter to strings only
    source_domains = [d for d in source_domains if isinstance(d, str) and d.strip()]
    if not source_domains:
        source_domains = defaults[:8] if defaults else default_domains[:8]

    return DecomposeResponse(
        business_type=raw.get("business_type", ""),
        location=location,
        target_customers=raw.get("target_customers", []),
        price_tier=raw.get("price_tier", ""),
        source_domains=source_domains[:8],
        subreddits=subreddits[:8],
        review_platforms=raw.get("review_platforms", ["yelp", "google"]),
        search_queries=queries[:8],
    )


def _preclean(text: str) -> str:
    return " ".join(text.strip().split())


def _infer_vertical(idea: str) -> str:
    idea_l = idea.lower()
    if any(k in idea_l for k in ["saas", "b2b", "api", "platform", "cloud", "developer", "ai tool", "security", "devops"]):
        return "saas_b2b"
    if any(k in idea_l for k in ["app", "mobile app", "consumer app", "marketplace", "subscription"]):
        return "consumer_app"
    if any(k in idea_l for k in ["restaurant", "bar", "cafe", "food", "kitchen", "juice", "coffee", "bakery"]):
        return "food_service"
    if any(k in idea_l for k in ["store", "shop", "salon", "clinic", "tutoring", "walking", "plumbing", "cleaning", "local", "repair"]):
        return "local_service"
    return "general"


def _default_domains_for_vertical(vertical: str) -> list[str]:
    match vertical:
        case "saas_b2b":
            return [
                "g2.com", "capterra.com", "producthunt.com",
                "news.ycombinator.com", "stackoverflow.com", "serverfault.com",
                "trustpilot.com", "amazon.com",
            ]
        case "consumer_app":
            return [
                "producthunt.com", "trustpilot.com", "news.ycombinator.com",
                "stackoverflow.com", "amazon.com",
            ]
        case "food_service":
            return [
                "yelp.com", "google.com/maps", "tripadvisor.com",
                "craigslist.org", "city-data.com/forum",
                "meetup.com", "eventbrite.com",
            ]
        case "local_service":
            return [
                "yelp.com", "google.com/maps", "craigslist.org",
                "city-data.com/forum", "nextdoor.com", "meetup.com",
            ]
        case _:
            return [
                "yelp.com", "google.com/maps", "trustpilot.com",
                "g2.com", "capterra.com", "producthunt.com",
                "news.ycombinator.com", "stackoverflow.com",
            ]


def _fallback_decompose(idea: str, vertical: str, defaults: list[str]) -> DecomposeResponse:
    loc = Location()
    return DecomposeResponse(
        business_type=idea[:80],
        location=loc,
        target_customers=[],
        price_tier="mid-range",
        source_domains=defaults[:8],
        subreddits=[],
        review_platforms=["yelp", "google"],
        search_queries=[
            f"{idea} reviews",
            f"{idea} complaints",
            f"{idea} alternatives",
        ],
    )


# Simple in-memory TTL cache with lock for thread-safety in async context
_cache_store: dict[str, tuple[float, DecomposeResponse]] = {}
_cache_lock = asyncio.Lock()


async def _cache_get(key: str) -> DecomposeResponse | None:
    async with _cache_lock:
        item = _cache_store.get(key)
        if not item:
            return None
        expires_at, val = item
        if time.time() > expires_at:
            _cache_store.pop(key, None)
            return None
        return val


async def _cache_set(key: str, val: DecomposeResponse) -> None:
    async with _cache_lock:
        _cache_store[key] = (time.time() + CACHE_TTL_SECONDS, val)


def _normalize_state(state: str) -> str:
    """Ensure state is 2-letter abbreviation."""
    state = state.strip().upper()
    # Common full names → abbreviations
    state_map = {
        "TEXAS": "TX", "CALIFORNIA": "CA", "NEW YORK": "NY",
        "FLORIDA": "FL", "ILLINOIS": "IL", "PENNSYLVANIA": "PA",
        "OHIO": "OH", "GEORGIA": "GA", "NORTH CAROLINA": "NC",
        "MICHIGAN": "MI", "NEW JERSEY": "NJ", "VIRGINIA": "VA",
        "WASHINGTON": "WA", "ARIZONA": "AZ", "MASSACHUSETTS": "MA",
        "TENNESSEE": "TN", "INDIANA": "IN", "MISSOURI": "MO",
        "MARYLAND": "MD", "WISCONSIN": "WI", "COLORADO": "CO",
        "MINNESOTA": "MN", "SOUTH CAROLINA": "SC", "ALABAMA": "AL",
        "LOUISIANA": "LA", "KENTUCKY": "KY", "OREGON": "OR",
        "OKLAHOMA": "OK", "CONNECTICUT": "CT", "UTAH": "UT",
        "IOWA": "IA", "NEVADA": "NV", "ARKANSAS": "AR",
        "MISSISSIPPI": "MS", "KANSAS": "KS", "NEW MEXICO": "NM",
        "NEBRASKA": "NE", "IDAHO": "ID", "WEST VIRGINIA": "WV",
        "HAWAII": "HI", "NEW HAMPSHIRE": "NH", "MAINE": "ME",
        "MONTANA": "MT", "RHODE ISLAND": "RI", "DELAWARE": "DE",
        "SOUTH DAKOTA": "SD", "NORTH DAKOTA": "ND", "ALASKA": "AK",
        "VERMONT": "VT", "WYOMING": "WY",
    }
    if state in state_map:
        return state_map[state]
    if len(state) == 2:
        return state
    return state[:2] if state else ""
