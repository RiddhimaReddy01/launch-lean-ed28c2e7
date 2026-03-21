"""
POST /api/decompose-idea
Converts raw idea string → structured searchable components.
Pipeline: Input validation → LLM extraction → Post-processing → Response
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from functools import lru_cache
import re
import time

from app.core.auth import optional_user
from app.schemas.models import DecomposeRequest, DecomposeResponse, Location
from app.services.llm_client import call_llm, AllProvidersExhaustedError
from app.prompts.templates import decompose_system, decompose_user

logger = logging.getLogger(__name__)
router = APIRouter()
CACHE_TTL_SECONDS = 900  # 15 minutes


@router.post("/api/decompose-idea", response_model=DecomposeResponse)
async def decompose_idea(
    req: DecomposeRequest,
    user: dict | None = Depends(optional_user),
):
    idea = _preclean(req.idea)

    # ── Stage 2: Input Cleaning ──
    if len(idea.split()) < 3:
        raise HTTPException(status_code=400, detail="Idea must be at least 3 words")

    # Stage 2.5: Cache check
    cached = _cache_get(idea)
    if cached:
        return cached

    # Infer vertical & defaults before LLM
    vertical = _infer_vertical(idea)
    defaults = _default_domains_for_vertical(vertical)

    # ── Stage 3: Build LLM Prompt ──
    system = decompose_system()
    user_prompt = decompose_user(idea, vertical, defaults)

    # ── Stage 4: LLM Call ──
    try:
        raw = await call_llm(
            system_prompt=system,
            user_prompt=user_prompt,
            temperature=0.1,
            max_tokens=800,
            json_mode=True,
        )
    except AllProvidersExhaustedError:
        # Fallback: deterministic template
        logger.warning("All LLM providers unavailable, using fallback decomposition")
        resp = _fallback_decompose(idea, vertical, defaults)
        _cache_set(idea, resp)
        return resp

    # ── Stage 5: Post-Processing ──
    resp = _post_process(raw, defaults)
    _cache_set(idea, resp)
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
        subreddits = [s.strip() for s in subreddits.split(",")]
    # Strip r/ prefix if present
    subreddits = [s.replace("r/", "").strip() for s in subreddits]
    # Pad with defaults if too few
    if len(subreddits) < 4 and location.city:
        defaults = [location.city.lower(), "smallbusiness", "Entrepreneur", "startups"]
        for d in defaults:
            if d not in subreddits and len(subreddits) < 4:
                subreddits.append(d)

    # Ensure search_queries has 5-8 entries
    queries = raw.get("search_queries", [])
    if isinstance(queries, str):
        queries = [queries]

    source_domains = raw.get("source_domains", [])
    if isinstance(source_domains, str):
        source_domains = [d.strip() for d in source_domains.split(",") if d.strip()]
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


# Simple in-memory TTL cache
_cache_store: dict[str, tuple[float, DecomposeResponse]] = {}


def _cache_get(key: str) -> DecomposeResponse | None:
    item = _cache_store.get(key)
    if not item:
        return None
    expires_at, val = item
    if time.time() > expires_at:
        _cache_store.pop(key, None)
        return None
    return val


def _cache_set(key: str, val: DecomposeResponse) -> None:
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
