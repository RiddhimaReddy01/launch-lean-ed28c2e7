"""
Run the full research pipeline for a fixed set of ideas and persist results.

This script uses the current in-process API handlers so the same validation,
cache writes, and response shaping happen as they would via HTTP.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from app.api.analyze import analyze_section
from app.api.decompose import decompose_idea
from app.api.discover import discover_insights
from app.api.setup import setup_section
from app.api.validate import generate_validation
from app.core.supabase import get_supabase
from app.schemas.models import (
    AnalyzeRequest,
    DecomposeRequest,
    DiscoverRequest,
    SetupRequest,
    ValidateRequest,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


USER_ID = "d23de268-412c-4b85-8fa9-29416047b765"
ANALYZE_SECTIONS = [
    "opportunity",
    "customers",
    "competitors",
    "rootcause",
    "costs",
    "risk",
    "location",
    "moat",
]
IDEAS = [
    "An authentic Thai street food restaurant in Dallas",
    "A fresh-pressed juice bar in Plano, Texas",
    "An AI-powered tutoring app for high school students",
]


def _safe_dump(value):
    if value is None:
        return None
    if hasattr(value, "model_dump"):
        return value.model_dump()
    return value


def _build_tags(idea: str) -> list[str]:
    raw = (
        idea.lower()
        .replace(",", "")
        .replace("  ", " ")
        .split()
    )
    stop_words = {
        "a", "an", "the", "for", "in", "of", "and", "to", "with",
    }
    tags = []
    for token in raw:
        if token in stop_words:
            continue
        if token not in tags:
            tags.append(token)
        if len(tags) >= 5:
            break
    return tags


async def run_one_idea(idea: str) -> dict:
    logger.info("Processing idea: %s", idea)

    decompose = await decompose_idea(DecomposeRequest(idea=idea), user=None)
    discover = await discover_insights(DiscoverRequest(idea=idea), user=None)

    top_insight = discover.insights[0].model_dump() if discover.insights else None
    decompose_dict = decompose.model_dump()

    analyze_results: dict[str, dict] = {}
    prior_context: dict[str, dict] = {}
    for section in ANALYZE_SECTIONS:
        logger.info("  Analyze section: %s", section)
        analyze_resp = await analyze_section(
            AnalyzeRequest(
                section=section,
                decomposition=decompose_dict,
                insight=top_insight,
                prior_context=prior_context or None,
            ),
            user=None,
        )
        analyze_results[section] = analyze_resp.data
        prior_context[section] = analyze_resp.data

    setup = await setup_section(
        SetupRequest(
            idea=idea,
            selected_tier="MID",
            prior_context={
                "costs": analyze_results.get("costs", {}),
                "root_causes": {"root_causes": analyze_results.get("rootcause", {}).get("root_causes", [])},
                "customers": analyze_results.get("customers", {}),
            },
        ),
        user=None,
    )

    validate = await generate_validation(
        ValidateRequest(
            idea=idea,
            channels=["landing_page", "survey", "whatsapp", "communities"],
            analysis_context=analyze_results,
            setup_context=setup.model_dump(),
        ),
        user=None,
    )

    return {
        "title": idea,
        "description": idea,
        "status": "completed",
        "decomposition": _safe_dump(decompose),
        "discover": _safe_dump(discover),
        "analyze": analyze_results,
        "setup": _safe_dump(setup),
        "validate": _safe_dump(validate),
        "tags": _build_tags(idea),
        "notes": "Cached via backend/cache_requested_queries.py",
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def save_idea_record(supabase, payload: dict) -> tuple[str, str]:
    title = payload["title"]

    existing = (
        supabase.table("ideas")
        .select("id")
        .eq("user_id", USER_ID)
        .eq("title", title)
        .limit(1)
        .execute()
    )

    if existing.data:
        idea_id = existing.data[0]["id"]
        response = (
            supabase.table("ideas")
            .update(payload)
            .eq("id", idea_id)
            .eq("user_id", USER_ID)
            .execute()
        )
        if not response.data:
            raise RuntimeError(f"Failed to update idea: {title}")
        return "updated", idea_id

    insert_payload = {
        "user_id": USER_ID,
        "created_at": datetime.now(timezone.utc).isoformat(),
        **payload,
    }
    response = supabase.table("ideas").insert(insert_payload).execute()
    if not response.data:
        raise RuntimeError(f"Failed to insert idea: {title}")
    return "inserted", response.data[0]["id"]


async def main():
    supabase = get_supabase()
    results = []

    for idea in IDEAS:
        try:
            payload = await run_one_idea(idea)
            action, idea_id = save_idea_record(supabase, payload)
            results.append({
                "idea": idea,
                "status": action,
                "idea_id": idea_id,
            })
            logger.info("Saved %s (%s)", idea, action)
        except Exception as exc:
            logger.exception("Failed processing %s", idea)
            results.append({
                "idea": idea,
                "status": "failed",
                "error": str(exc),
            })

    print("\nRESULTS")
    for item in results:
        print(item)


if __name__ == "__main__":
    asyncio.run(main())
