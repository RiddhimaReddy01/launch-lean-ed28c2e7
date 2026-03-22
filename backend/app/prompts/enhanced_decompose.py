"""
Enhanced decomposition prompts with better context and constraints.
Improves LLM understanding of business ideas for accurate extraction.
"""


def decompose_stage2_enhanced(
    idea: str,
    business_type: str,
    city: str,
    state: str,
    vertical: str,
    pre_analysis: dict,
    domain_suggestions: list[str],
) -> str:
    """
    Enhanced Stage 2 prompt with more context and constraints.

    Provides:
    - Pre-analyzed entity signals
    - Vertical-specific guidance
    - Market research context
    - Constraint instructions
    """

    location_str = f"{city}, {state}" if city and state else (city or state or "nationwide")
    domains = ", ".join(domain_suggestions[:10])

    # Build context from pre-analysis
    context_lines = []

    if pre_analysis.get("has_location"):
        context_lines.append(f"Location is SPECIFIC: {location_str}")
        context_lines.append("→ Prioritize LOCAL domains (yelp, google maps, nextdoor)")
    else:
        context_lines.append("Location is BROAD or NATIONAL")
        context_lines.append("→ Prioritize GLOBAL domains (g2, producthunt, trustpilot)")

    if pre_analysis.get("business_model"):
        context_lines.append(f"Business Model: {pre_analysis['business_model'].upper()}")

    if pre_analysis.get("market_size_hint"):
        context_lines.append(f"Market Size: {pre_analysis['market_size_hint'].upper()}")

    context_str = "\n".join(context_lines)

    # Build vertical-specific guidance
    vertical_guidance = {
        "saas_b2b": """
For B2B/SaaS businesses:
- Target customers should include: business types, team sizes, or roles (e.g., "product managers", "engineering teams")
- Price tier should mention: per-user pricing, annual contracts, or free tier
- Source domains MUST include: g2.com, capterra.com, producthunt.com
- Search queries should focus on: comparisons, alternatives, reviews, ROI
""",
        "food_service": """
For Food/Restaurant/Bar businesses:
- Target customers should include: demographics + eating habits (e.g., "health-conscious professionals", "night-life seekers")
- Price tier should mention: price per item/meal and order value
- Source domains MUST include: yelp.com, google.com/maps, tripadvisor.com, instagram.com
- Search queries should focus on: local reviews, delivery options, competitors nearby
- Subreddits should be local + food-related (r/foodit, r/sanfrancisco, etc)
""",
        "local_service": """
For Local Services (cleaning, plumbing, tutoring, etc):
- Target customers should include: local demographic specifics (e.g., "busy professionals", "elderly homeowners")
- Price tier should mention: hourly rates, per-project costs, or subscription
- Source domains MUST include: yelp.com, google.com/maps, nextdoor.com, craigslist.org
- Search queries should focus on: local competitors, service demand, customer pain points
- Subreddits should be LOCAL (r/sanfrancisco, r/AskLosAngeles, etc)
""",
        "marketplace": """
For Marketplace/C2C platforms:
- Target customers should include: both SUPPLY side and DEMAND side (e.g., "freelancers" AND "companies seeking talent")
- Price tier should mention: transaction fees, subscription tiers, or commission
- Source domains MUST include: producthunt.com, trustpilot.com, crunchbase.com
- Search queries should focus on: competitor marketplaces, user demand signals, supply availability
""",
    }

    vertical_hint = vertical_guidance.get(vertical, "")

    return f"""
CONTEXT:
{context_str}

BUSINESS IDEA: {idea}
Business Type Extracted: {business_type}
Vertical: {vertical.upper()}

{vertical_hint}

TASK: Extract detailed market research components for this {vertical} business.

IMPORTANT CONSTRAINTS:
1. Target Customers (2-4 items):
   - Be SPECIFIC: Include demographics, behaviors, or pain points
   - Example: "Busy urban professionals" NOT just "working professionals"
   - Example: "DIY enthusiasts with home improvement projects" NOT just "homeowners"

2. Price Tier (should include currency range):
   - Example: "premium ($15-25/month subscription)" NOT just "premium"
   - Example: "budget ($200-500 per service call)" for local services
   - If unsure, estimate based on vertical

3. Source Domains (4-8, pick from suggestions):
   - PRIORITIZE {vertical.upper()} domains from suggestions
   - Recommended: {domains}

4. Search Queries (5-8, specific and actionable):
   - Each query should target: competitors, reviews, pain points, OR alternative solutions
   - Example queries for tutoring:
     * "online tutoring platform reviews"
     * "AI tutor high school students"
     * "alternative to traditional tutoring"
     * "affordable homework help software"

5. Subreddits (optional, leave empty if not relevant):
   - Only include if this business would have community discussion
   - Be SPECIFIC: r/learnprogramming, not just r/learning

Return ONLY valid JSON with these exact keys:
{{
  "target_customers": ["specific customer segment", "another segment"],
  "price_tier": "tier_level ($min-$max)",
  "source_domains": ["domain1.com", "domain2.com"],
  "subreddits": ["subreddit_name"],
  "review_platforms": ["platform_name"],
  "search_queries": ["query1", "query2", "query3"]
}}
"""


def pre_analyze_idea(idea: str) -> dict:
    """
    Pre-analyze idea to extract structured signals BEFORE sending to LLM.
    Helps guide LLM with concrete facts rather than vague requests.
    """
    import re

    idea_lower = idea.lower()

    # Location detection
    us_cities = [
        "san francisco", "los angeles", "new york", "austin", "seattle",
        "boston", "denver", "chicago", "miami", "portland", "oakland",
        "sf", "la", "nyc", "dc", "sf bay"
    ]
    us_states = [
        "california", "texas", "new york", "florida", "washington",
        "colorado", "illinois", "massachusetts", "ca", "tx", "ny", "fl", "wa"
    ]

    has_location = False
    location_hint = ""
    for city in us_cities:
        if city in idea_lower:
            has_location = True
            location_hint = city.title()
            break
    if not has_location:
        for state in us_states:
            if state in idea_lower:
                has_location = True
                location_hint = state.title()

    # Business model detection
    b2b_keywords = ["saas", "api", "platform", "software", "ai", "ml", "tool", "service for business"]
    b2c_keywords = ["app", "consumer", "marketplace", "subscription", "delivery"]
    local_keywords = ["local", "near", "in-home", "on-site", "neighborhood", "community"]

    business_model = "unknown"
    if any(kw in idea_lower for kw in b2b_keywords):
        business_model = "B2B"
    elif any(kw in idea_lower for kw in b2c_keywords):
        business_model = "B2C"

    if any(kw in idea_lower for kw in local_keywords):
        business_model = "LOCAL"

    # Market size hint
    market_size_hint = "regional"
    if "global" in idea_lower or "worldwide" in idea_lower:
        market_size_hint = "global"
    elif has_location:
        market_size_hint = "local"
    elif "national" in idea_lower or "nationwide" in idea_lower:
        market_size_hint = "national"

    # Urgency level
    urgency_keywords = {
        "seasonal": ["summer", "winter", "holiday", "seasonal"],
        "urgent": ["emergency", "critical", "immediate", "urgent"],
    }
    urgency_level = "evergreen"
    for level, keywords in urgency_keywords.items():
        if any(kw in idea_lower for kw in keywords):
            urgency_level = level
            break

    # Extract key terms
    words = idea_lower.split()
    key_terms = [w.strip(".,!?") for w in words if len(w) > 4]

    # Detect pain points (implied from context)
    pain_point_keywords = [
        "expensive", "slow", "complicated", "hard to find", "lacking",
        "no alternative", "struggling", "problem with", "frustrated with"
    ]
    pain_points = [kw for kw in pain_point_keywords if kw in idea_lower]

    return {
        "has_location": has_location,
        "location_hint": location_hint,
        "has_target_audience": any(kw in idea_lower for kw in ["for", "targeting", "serving"]),
        "has_business_model": True,
        "business_model": business_model,
        "market_size_hint": market_size_hint,
        "urgency_level": urgency_level,
        "key_terms": key_terms[:10],  # Top 10 terms
        "pain_points": pain_points,
    }


# Example usage in decompose.py:
"""
from app.prompts.enhanced_decompose import decompose_stage2_enhanced, pre_analyze_idea

# In decompose_idea endpoint:
pre_analysis = pre_analyze_idea(idea)
stage2_prompt = decompose_stage2_enhanced(
    idea=idea,
    business_type=business_type,
    city=stage1_location.city,
    state=stage1_location.state,
    vertical=vertical,
    pre_analysis=pre_analysis,
    domain_suggestions=defaults,
)

stage2_raw = await call_llm(
    system_prompt=decompose_stage2_system(),
    user_prompt=stage2_prompt,
    temperature=0.05,
    max_tokens=500,
    json_mode=True,
)
"""
