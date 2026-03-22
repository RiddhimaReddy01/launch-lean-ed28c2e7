"""
Google Search via Serper.dev API.
2,500 free searches/month, no credit card required.
Returns clean JSON with organic results, snippets, and metadata.
"""

import logging
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

SERPER_URL = "https://google.serper.dev/search"
REQUEST_TIMEOUT = 10.0


async def serper_search(
    client: httpx.AsyncClient,
    query: str,
    num: int = 10,
    location: str | None = None,
) -> list[dict]:
    """
    Run a single Google search via Serper.dev.
    Returns list of organic results with title, snippet, link.
    """
    if not settings.SERPER_API_KEY:
        logger.warning("SERPER_API_KEY not set, skipping search")
        return []

    body = {"q": query, "num": num}
    if location:
        body["location"] = location

    try:
        resp = await client.post(
            SERPER_URL,
            headers={
                "X-API-KEY": settings.SERPER_API_KEY,
                "Content-Type": "application/json",
            },
            json=body,
            timeout=REQUEST_TIMEOUT,
        )

        if resp.status_code == 429:
            logger.warning("Serper rate limit hit")
            return []
        if resp.status_code != 200:
            logger.warning(f"Serper returned {resp.status_code}: {resp.text[:200]}")
            return []

        data = resp.json()
        organic = data.get("organic", [])

        results = []
        for r in organic:
            results.append({
                "title": r.get("title", ""),
                "snippet": r.get("snippet", ""),
                "link": r.get("link", ""),
                "position": r.get("position", 0),
                "source": "google_search",
            })

        return results

    except (httpx.TimeoutException, httpx.HTTPError) as e:
        logger.warning(f"Serper search failed for '{query}': {e}")
        return []


async def run_search_queries(
    queries: list[str],
    location: str | None = None,
    num_per_query: int = 10,
) -> list[dict]:
    """
    Run multiple search queries and return combined results.
    Tags each result with the query that produced it.
    """
    all_results = []

    async with httpx.AsyncClient() as client:
        for query in queries:
            results = await serper_search(
                client, query, num=num_per_query, location=location
            )
            for r in results:
                r["query"] = query
            all_results.extend(results)

    logger.info(f"Serper: {len(all_results)} results from {len(queries)} queries")
    return all_results


def build_discover_queries(decomposition: dict) -> list[str]:
    """Build search queries for Module 1 (Discover) based on idea decomposition."""
    btype = decomposition.get("business_type", "")
    loc = decomposition.get("location", {})
    city = loc.get("city", "")
    state = loc.get("state", "")
    metro = loc.get("metro", "")
    domains = decomposition.get("source_domains", []) or []

    default_domains = [
        "yelp.com", "google.com/maps", "trustpilot.com",
        "g2.com", "capterra.com", "producthunt.com",
        "news.ycombinator.com", "stackoverflow.com",
        "craigslist.org", "meetup.com", "eventbrite.com",
        "tripadvisor.com", "city-data.com/forum", "amazon.com",
    ]

    if not domains:
        domains = default_domains

    queries = []

    # Top priority: site searches on review platforms (most relevant)
    review_domains = [d for d in domains[:6] if any(r in d for r in ["yelp", "google", "trustpilot", "tripadvisor"])]
    for d in review_domains[:3]:
        queries.append(f"{btype} {city} {state} site:{d}")

    # Pain point queries (high signal for market research)
    queries.append(f'"{btype}" "{city}" complaints bad reviews -site:reddit.com')
    queries.append(f'"{btype}" "{city}" problems issues frustration')
    queries.append(f'"{btype}" "{city}" alternatives competitors pricing')

    # Local and pricing queries
    queries.append(f"best {btype} near {city} {state}")
    queries.append(f"{btype} {city} {state} prices cost overpriced")
    queries.append(f"{btype} {city} {state} hours location wait times")

    return queries[:8]


def build_competitor_queries(decomposition: dict) -> list[str]:
    """Build search queries for Module 2 Section C (Competitors)."""
    btype = decomposition.get("business_type", "")
    loc = decomposition.get("location", {})
    city = loc.get("city", "")
    state = loc.get("state", "")

    queries = [
        f"{btype} near {city} {state} site:yelp.com",
        f"best {btype} {city} {state}",
        f"{btype} {city} {state} reviews",
        f"new {btype} opening {city} 2025 2026",
    ]
    return queries


def build_setup_queries(decomposition: dict) -> list[str]:
    """Build search queries for Module 3 (Setup) - suppliers, costs, permits."""
    btype = decomposition.get("business_type", "")
    loc = decomposition.get("location", {})
    city = loc.get("city", "")
    state = loc.get("state", "")
    metro = loc.get("metro", "")

    queries = [
        f"{btype} equipment supplier {metro}",
        f"commercial lease {city} {state} 2026",
        f"{btype} permits licenses {city} {state}",
        f"wholesale supplier {btype} {state}",
        f"{btype} POS system point of sale",
    ]
    return queries


def build_community_queries(decomposition: dict) -> list[str]:
    """Build search queries for Module 4 (Validate) - community discovery."""
    btype = decomposition.get("business_type", "")
    loc = decomposition.get("location", {})
    city = loc.get("city", "")
    state = loc.get("state", "")
    metro = loc.get("metro", "")

    queries = [
        f"{btype} {city} Facebook group",
        f"{btype} {metro} Discord server",
        f"{city} entrepreneurs small business network",
        f"{city} {state} food community OR recommendations Nextdoor",
    ]
    return queries
