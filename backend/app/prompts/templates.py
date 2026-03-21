"""
All system prompts for LaunchLens LLM calls.
Each prompt is a function that takes context and returns a formatted string.
"""


# ═══ MODULE 0: DECOMPOSE IDEA ═══


def decompose_system() -> str:
    return """You are a startup idea decomposition engine. Given a business idea description, extract structured searchable components.

Return ONLY valid JSON with these exact keys:
{
  "business_type": "string - what kind of business (be specific, include 2-3 variants)",
  "location": {
    "city": "string",
    "state": "string (2-letter abbreviation)",
    "county": "string",
    "metro": "string (metro area name)"
  },
  "target_customers": ["string array - 2-4 customer segments"],
  "price_tier": "string (budget/mid-range/premium with estimated $ range)",
  "source_domains": ["string array - 4-8 domains to search, choose from: yelp.com, google.com/maps, trustpilot.com, g2.com, capterra.com, producthunt.com, news.ycombinator.com, stackoverflow.com, serverfault.com, craigslist.org, meetup.com, eventbrite.com, tripadvisor.com, city-data.com/forum, amazon.com"],
  "subreddits": ["string array - optional, leave empty if not important"],
  "review_platforms": ["string array - relevant review platforms (yelp, google, etc.)"],
  "search_queries": ["string array - 5-8 Google search queries to find competitors, reviews, community discussions, and pain points for this exact business type and location"]
}

Be specific to the location. Prefer source_domains over subreddits for community and review signals."""


def decompose_user(idea: str, vertical: str, domain_suggestions: list[str]) -> str:
    domains = ", ".join(domain_suggestions[:10])
    return (
        "Decompose this startup idea into searchable components.\n\n"
        f"Idea: \"{idea}\"\n"
        f"Inferred vertical: {vertical}\n"
        f"Recommended domains to choose from (pick 6-8): {domains}\n"
    )


# ═══ MODULE 1: DISCOVER ═══


def discover_categorize_system(business_type: str, city: str, state: str) -> str:
    return f"""You are analyzing real community data about a {business_type} in {city}, {state}.

Analyze the posts and search results provided. Your task:

1. IDENTIFY distinct insights (NOT individual posts). Group similar complaints, wants, or observations into unified insights.
2. CATEGORIZE each insight as exactly one of: pain_point, unmet_want, market_gap, trend
3. For each insight, select 2-3 ACTUAL quotes from the provided data as evidence. These MUST be real text from the posts - do NOT invent quotes.
4. Tag each insight with the source platforms it appeared on.
5. Estimate the affected audience size where possible.

Return JSON:
{{
  "insights": [
    {{
      "type": "pain_point | unmet_want | market_gap | trend",
      "title": "Clear, concise title (5-10 words)",
      "evidence": [
        {{
          "quote": "Actual text from a post",
          "source": "subreddit name or search source",
          "score": 0
        }}
      ],
      "source_platforms": ["reddit", "yelp"],
      "audience_estimate": "rough estimate string",
      "frequency": 0,
      "intensity_note": "brief description of how strongly people feel"
    }}
  ]
}}

Target: 8-15 insights. Merge highly similar ones. Prioritize insights with strong evidence."""


def discover_categorize_user(posts: list[dict], post_count: int, include_score: bool = False) -> str:
    # Build condensed post list for LLM
    lines = []
    for i, post in enumerate(posts[:200]):
        src = post.get("subreddit", post.get("query_type", "search"))
        title = post.get("title", "")
        body = post.get("body", post.get("snippet", ""))[:160]
        score = post.get("score", 0)
        lines.append(f"[{i+1}] [{src}] (score:{score}) {title}")
        if body:
            lines.append(f"    {body}")
    post_text = "\n".join(lines)

    extra = ""
    if include_score:
        extra = "\nAlso score each insight with frequency_score, intensity_score, willingness_to_pay_score (1-10) and pain_score (weighted). Keep 8-12 insights."

    return f"""Here are {post_count} posts/results from Reddit, Yelp, Google, and Nextdoor about this business in the local area:

{post_text}

Analyze these and identify the key customer insights.{extra}"""


def discover_score_system() -> str:
    return """You are scoring startup customer insights. For each insight, calculate:

pain_score = (frequency * 0.4) + (intensity * 0.35) + (willingness_to_pay * 0.25)

Where each factor is rated 1-10:
- frequency: How often this appears across the data sources (1=rare, 10=very common)
- intensity: How strongly people feel about it (1=mild annoyance, 10=angry/desperate)
- willingness_to_pay: Evidence that people would spend money to solve this (1=no signal, 10=explicit spending intent)

Return the same insights array but with these additional fields on each:
{
  "insights": [
    {
      ...existing fields...,
      "frequency_score": 1-10,
      "intensity_score": 1-10,
      "willingness_to_pay_score": 1-10,
      "pain_score": calculated float (0-10)
    }
  ]
}

Sort by pain_score descending (highest pain first)."""


def discover_score_user(insights_json: str) -> str:
    return f"""Score and rank these customer insights:

{insights_json}"""


# ═══ MODULE 2: ANALYZE ═══


def analyze_opportunity_system(business_type: str, city: str, state: str, metro: str) -> str:
    return f"""Calculate market sizing for a {business_type} in {city}, {state} ({metro} metro area).

Using the market data provided and your knowledge of the area, calculate:
- TAM: Total addressable market for this business type in {metro}
- SAM: Serviceable available market matching the specific pain point
- SOM: Serviceable obtainable market - realistic year-1 capture for a single new location

Return JSON:
{{
  "tam": {{
    "value": dollar amount as number,
    "formatted": "$X.XM or $XB",
    "methodology": "2-3 sentence explanation",
    "confidence": "low | medium | high"
  }},
  "sam": {{ same structure }},
  "som": {{ same structure }},
  "funnel": {{
    "population": number,
    "aware": number,
    "interested": number,
    "willing_to_try": number,
    "repeat_customers": number
  }}
}}

Be specific to {city}, {state}. Use real population data for {metro}."""


def analyze_customers_system(business_type: str, city: str) -> str:
    return f"""Generate 3-4 customer segments for a {business_type} in {city} based on the customer evidence provided.

For each segment, return:
{{
  "segments": [
    {{
      "name": "Segment name (2-4 words)",
      "description": "2-3 sentences about who they are",
      "estimated_size": number (people in this segment locally),
      "pain_intensity": 1-10,
      "primary_need": "What they care about most",
      "spending_pattern": "How much/often they currently spend on alternatives",
      "where_to_find": "Where this segment hangs out (online + offline)"
    }}
  ]
}}

Sort by pain_intensity descending."""


def analyze_competitors_system(business_type: str, city: str, state: str) -> str:
    return f"""Analyze competitors for a {business_type} in {city}, {state}.

Using the search results and review data provided, analyze each competitor:
{{
  "competitors": [
    {{
      "name": "Business name",
      "location": "Specific location/address if available",
      "rating": star rating or null,
      "price_range": "$/$$/$$$ or specific range",
      "key_strength": "What they do well (1 sentence)",
      "key_gap": "What they miss - use evidence from reviews (1-2 sentences)",
      "threat_level": "low | medium | high",
      "url": "Yelp or Google link if available"
    }}
  ],
  "unfilled_gaps": [
    "Gap that NO competitor fills (2-3 of these)"
  ]
}}

Include 4-8 competitors. Sort by threat_level (high first)."""


def analyze_rootcause_system(business_type: str, city: str, state: str) -> str:
    return f"""You are a startup strategist analyzing WHY a market gap exists for a {business_type} in {city}, {state}.

Identify 3-5 ROOT CAUSES for why this gap still exists. These should be structural, economic, or regulatory reasons — NOT just "nobody thought of it."

Return JSON:
{{
  "root_causes": [
    {{
      "cause_number": 1,
      "title": "Concise title (e.g., 'Franchise lease lock-out')",
      "explanation": "2-3 sentences with specific evidence about {city}/{state}",
      "your_move": "Specific, actionable counter-strategy for the founder. Reference real locations, tactics, or approaches specific to {city}.",
      "difficulty": "easy | medium | hard"
    }}
  ]
}}

This is the MOST DIFFERENTIATED analysis section. Go deep. Reference local specifics."""


def analyze_costs_preview_system(business_type: str, city: str, state: str) -> str:
    return f"""Give a quick cost estimate for launching a {business_type} in {city}, {state}.

Return JSON:
{{
  "total_range": {{ "min": number, "max": number }},
  "breakdown": [
    {{ "category": "Real Estate", "min": number, "max": number }},
    {{ "category": "Equipment", "min": number, "max": number }},
    {{ "category": "Permits & Legal", "min": number, "max": number }},
    {{ "category": "Initial Operations", "min": number, "max": number }}
  ],
  "note": "One sentence about the biggest cost driver"
}}

Be specific to {city}, {state} commercial rates."""


def analyze_section_user(section: str, insight: dict, decomposition: dict, extra_context: str = "") -> str:
    insight_title = insight.get("title", "Unknown insight")
    evidence_text = ""
    for ev in insight.get("evidence", [])[:5]:
        evidence_text += f"  - \"{ev.get('quote', '')}\" (from {ev.get('source', 'unknown')})\n"

    base = f"""Business: {decomposition.get('business_type', '')}
Location: {decomposition.get('location', {}).get('city', '')}, {decomposition.get('location', {}).get('state', '')}
Target customers: {', '.join(decomposition.get('target_customers', []))}

Selected insight: {insight_title}
Evidence:
{evidence_text}"""

    if extra_context:
        base += f"\n\nAdditional context:\n{extra_context}"

    return base


# ═══ MODULE 3: SETUP ═══


def setup_system(business_type: str, city: str, state: str, metro: str) -> str:
    return f"""Generate a complete launch plan for a {business_type} in {city}, {state} ({metro} metro).

Return JSON with these sections:

{{
  "cost_tiers": [
    {{
      "tier": "minimum_viable | recommended | full_buildout",
      "model": "Description (e.g., 'Kiosk or food hall')",
      "total_range": {{ "min": number, "max": number }},
      "line_items": [
        {{
          "category": "real_estate | equipment | permits_legal | initial_operations | runway_3mo",
          "name": "Specific item name",
          "min_cost": number,
          "max_cost": number,
          "notes": "Brief note"
        }}
      ]
    }}
  ],
  "suppliers": [
    {{
      "category": "produce | equipment | packaging | services | technology",
      "name": "Real company name",
      "description": "What they provide",
      "location": "City/area",
      "website": "URL if known",
      "why_recommended": "1 sentence"
    }}
  ],
  "team": [
    {{
      "title": "Role title",
      "type": "full_time | part_time | contract",
      "salary_range": {{ "min": number, "max": number }},
      "priority": "must_have | nice_to_have",
      "tier": "minimum_viable | recommended | full_buildout"
    }}
  ],
  "timeline": [
    {{
      "phase": "Phase name",
      "weeks": "1-2",
      "milestones": ["string array of 3-4 key milestones"]
    }}
  ]
}}

CRITICAL: Use {city}, {state} specific data:
- Real commercial lease rates for {city}
- {state} specific permit costs and requirements
- {metro} labor market salary ranges
- Real local supplier names where possible"""


def setup_user(decomposition: dict, insight: dict, analysis_summary: str, search_data: str) -> str:
    return f"""Generate a launch plan for this business:

Type: {decomposition.get('business_type', '')}
Location: {decomposition.get('location', {}).get('city', '')}, {decomposition.get('location', {}).get('state', '')}
Key insight: {insight.get('title', '')}

Market analysis summary:
{analysis_summary}

Local supplier/cost search results:
{search_data}"""


# ═══ MODULE 4: VALIDATE ═══


def validate_system(business_type: str, city: str, state: str) -> str:
    return f"""Generate demand validation materials for a {business_type} in {city}, {state}.

CRITICAL: Use the EXACT pain language from the customer quotes provided. The landing page copy should sound like the customers, not like a marketer.

Return JSON:
{{
  "landing_page": {{
    "headline": "Attention-grabbing headline using #1 pain point",
    "subheadline": "Promise the solution in one sentence",
    "benefits": ["3-4 bullet points using customer language"],
    "cta_text": "Action-oriented button text",
    "social_proof_quote": "A real quote from Module 1 evidence"
  }},
  "survey": {{
    "title": "Survey title",
    "questions": [
      {{
        "number": 1,
        "question": "Question text",
        "type": "multiple_choice | scale | open_text | email",
        "options": ["array of options if multiple_choice, null otherwise"]
      }}
    ]
  }},
  "whatsapp_message": {{
    "message": "Casual, shareable message for local groups. Include [SURVEY_LINK] placeholder.",
    "tone_note": "Brief note on tone"
  }},
  "communities": [
    {{
      "name": "Community/group name",
      "platform": "facebook | discord | nextdoor | reddit | other",
      "member_count": "estimated count string or null",
      "rationale": "Why share here (1 sentence)",
      "link": "Direct link if known"
    }}
  ],
  "scorecard": {{
    "waitlist_target": number,
    "survey_target": 50,
    "switch_pct_target": 60,
    "price_tolerance_target": "Above $X (minimum viable price)"
  }}
}}

Generate exactly 7 survey questions in this order:
1. Frequency of current purchases
2. Current solution / where they go now
3. Biggest frustration (open text)
4. Willingness to switch (yes/no/maybe)
5. Price sensitivity (range options)
6. Location preference (multiple choice)
7. Email capture for launch updates"""


def validate_user(
    decomposition: dict,
    insight: dict,
    pain_language: list[str],
    analysis_summary: str,
    setup_summary: str,
    community_search_data: str,
    channels: list[str],
) -> str:
    pain_quotes = "\n".join(f'  - "{q}"' for q in pain_language[:10])

    return f"""Generate validation materials for:

Business: {decomposition.get('business_type', '')}
Location: {decomposition.get('location', {}).get('city', '')}, {decomposition.get('location', {}).get('state', '')}
Key insight: {insight.get('title', '')}

CUSTOMER PAIN LANGUAGE (use these exact phrases in the landing page):
{pain_quotes}

Market context:
{analysis_summary}

Launch plan context:
{setup_summary}

Community search results:
{community_search_data}

Selected channels: {', '.join(channels)}"""
