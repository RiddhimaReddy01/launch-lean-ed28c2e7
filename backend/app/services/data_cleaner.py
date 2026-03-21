"""
Deterministic data cleaning for all ingested sources.
No LLM calls - pure Python filtering, dedup, normalization.
"""

import re
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


# ─── Reddit Post Cleaning ─────────────────────────────────────────────


def clean_reddit_posts(raw_posts: list[dict]) -> list[dict]:
    """
    Clean and filter Reddit posts. Deterministic pipeline:
    1. Filter low-signal posts (score < 3, comments < 2)
    2. Remove deleted/removed content
    3. Remove media-only posts
    4. Deduplicate by normalized title
    5. Truncate body to 500 chars
    """
    cleaned = []
    seen_titles: set[str] = set()

    for post in raw_posts:
        # FILTER 1: Low-signal posts
        if post.get("score", 0) < 3:
            continue
        if post.get("num_comments", 0) < 2:
            continue

        # FILTER 2: Deleted/removed content
        body = post.get("body", "") or ""
        title = post.get("title", "") or ""
        if body in ("[removed]", "[deleted]"):
            body = ""
        if not title and not body:
            continue

        # FILTER 3: Media-only posts (no useful text for LLM)
        if post.get("is_video") or post.get("post_hint") in ("image", "hosted:video", "rich:video"):
            if not body:
                continue

        # DEDUP: Normalize title, skip if seen
        norm_title = _normalize_text(title)
        if norm_title in seen_titles and norm_title:
            continue
        if norm_title:
            seen_titles.add(norm_title)

        # TRUNCATE: Cap body at 500 chars to save LLM tokens
        body = body[:500]

        cleaned.append({
            "title": title,
            "body": body,
            "score": post.get("score", 0),
            "num_comments": post.get("num_comments", 0),
            "subreddit": post.get("subreddit", ""),
            "created_date": post.get("created_date", "unknown"),
            "permalink": post.get("permalink", ""),
            "source": "reddit",
        })

    logger.info(f"Reddit cleaning: {len(raw_posts)} raw -> {len(cleaned)} cleaned")
    return cleaned


# ─── Google Search Result Cleaning ─────────────────────────────────────


def clean_search_results(raw_results: list[dict], query_type: str = "general") -> list[dict]:
    """
    Clean Google search results from Serper.
    Dedup by URL, filter irrelevant domains, extract ratings/prices.
    """
    cleaned = []
    seen_links: set[str] = set()

    # Domains to always filter out
    blocked_domains = {
        "pinterest.com", "facebook.com/login", "tiktok.com",
        "instagram.com",
    }

    platform_map = {
        "yelp.com": "yelp_web",
        "google.com": "google_reviews_web",
        "maps.google.com": "google_reviews_web",
        "trustpilot.com": "trustpilot",
        "g2.com": "g2",
        "capterra.com": "capterra",
        "producthunt.com": "producthunt",
        "news.ycombinator.com": "hackernews",
        "stackoverflow.com": "stackoverflow",
        "serverfault.com": "serverfault",
        "craigslist.org": "craigslist",
        "meetup.com": "meetup",
        "eventbrite.com": "eventbrite",
        "tripadvisor.com": "tripadvisor",
        "city-data.com": "citydata",
        "amazon.com": "amazon",
        "twitter.com": "twitter",
        "x.com": "twitter",
    }

    for r in raw_results:
        link = r.get("link", "")

        # DEDUP by URL
        if link in seen_links:
            continue
        seen_links.add(link)

        # FILTER: Blocked domains
        if any(d in link for d in blocked_domains):
            continue

        snippet = r.get("snippet", "") or ""
        domain = urlparse(link).netloc.lower()
        platform = None
        for key, val in platform_map.items():
            if key in domain:
                platform = val
                break

        # EXTRACT: Star rating from snippet (e.g., "4.5 stars", "Rating: 4.2")
        rating = _extract_star_rating(snippet)

        # EXTRACT: Price range from snippet (e.g., "$", "$$", "$10-15")
        price_range = _extract_price_range(snippet)

        cleaned.append({
            "title": r.get("title", ""),
            "snippet": snippet[:300],
            "link": link,
            "rating": rating,
            "price_range": price_range,
            "query_type": query_type,
            "query": r.get("query", ""),
            "source": "google_search",
            "platform": platform or "web",
            "domain": domain,
        })

    logger.info(f"Search cleaning: {len(raw_results)} raw -> {len(cleaned)} cleaned")
    return cleaned


# ─── Merge & Transform ────────────────────────────────────────────────


def merge_all_sources(
    reddit_posts: list[dict],
    search_results: list[dict],
    max_items: int = 200,
) -> list[dict]:
    """
    Merge Reddit posts and search results into a single list.
    Sort by signal strength (score for Reddit, position for search).
    Cap at max_items for LLM context window management.
    """
    combined = reddit_posts + search_results
    # Sort: Reddit by score desc, search by position asc (lower = better)
    combined.sort(
        key=lambda x: x.get("score", 0) if x["source"] == "reddit" else (100 - x.get("position", 50)),
        reverse=True,
    )
    return combined[:max_items]


def build_source_summary(posts: list[dict]) -> list[dict]:
    """Build per-source summary for the frontend source bar."""
    sources: dict[str, dict] = {}
    for post in posts:
        if post["source"] == "reddit":
            key = f"r/{post.get('subreddit', 'unknown')}"
            src_type = "reddit"
        else:
            key = post.get("platform") or post.get("domain") or post.get("query_type", "web")
            src_type = post.get("platform") or "web"

        if key not in sources:
            sources[key] = {"name": key, "type": src_type, "post_count": 0}
        sources[key]["post_count"] += 1

    return list(sources.values())


# ─── Helpers ──────────────────────────────────────────────────────────


def _normalize_text(text: str) -> str:
    """Normalize text for dedup comparison."""
    t = text.lower().strip()
    t = re.sub(r"[^\w\s]", "", t)  # remove punctuation
    t = re.sub(r"\s+", " ", t)  # collapse whitespace
    return t


def _extract_star_rating(text: str) -> float | None:
    """Extract star rating from text (e.g., '4.5 stars', 'Rating: 4.2')."""
    patterns = [
        r"(\d\.\d)\s*(?:star|rating|\u2605)",
        r"(?:rating|rated)[\s:]*(\d\.\d)",
        r"(\d\.\d)\s*/\s*5",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                rating = float(match.group(1))
                if 1.0 <= rating <= 5.0:
                    return rating
            except ValueError:
                continue
    return None


def _extract_price_range(text: str) -> str | None:
    """Extract price range indicator from text."""
    # Match $$$ style
    match = re.search(r"(\${1,4})", text)
    if match:
        return match.group(1)
    # Match "$X - $Y" style
    match = re.search(r"\$(\d+)\s*[-\u2013]\s*\$(\d+)", text)
    if match:
        return f"${match.group(1)}-${match.group(2)}"
    return None


def extract_dollar_figures(text: str) -> list[dict]:
    """Extract dollar amounts and context from text (for market sizing)."""
    figures = []
    patterns = [
        (r"\$(\d+(?:\.\d+)?)\s*(billion|B)\b", 1_000_000_000),
        (r"\$(\d+(?:\.\d+)?)\s*(million|M)\b", 1_000_000),
        (r"\$(\d+(?:\.\d+)?)\s*(thousand|K)\b", 1_000),
        (r"\$(\d{1,3}(?:,\d{3})+)", 1),  # $1,234,567
    ]
    for pattern, multiplier in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            try:
                num_str = match.group(1).replace(",", "")
                value = float(num_str) * multiplier
                # Get surrounding context
                start = max(0, match.start() - 40)
                end = min(len(text), match.end() + 40)
                context = text[start:end].strip()
                figures.append({"value": value, "context": context})
            except ValueError:
                continue
    return figures
