"""
All system prompts for LaunchLens LLM calls.
Each prompt is a function that takes context and returns a formatted string.
"""


# ═══ MODULE 0: DECOMPOSE IDEA ═══


def decompose_system() -> str:
    return """You are a startup idea decomposition engine. Extract structured searchable components for market research.

Return ONLY valid JSON with these exact keys:
{
  "business_type": "string - specific business description (2-3 words, be concrete)",
  "location": {
    "city": "string or empty",
    "state": "string (2-letter abbreviation) or empty",
    "county": "string or empty",
    "metro": "string or empty"
  },
  "target_customers": ["string array - 2-4 customer segments"],
  "price_tier": "string (budget/mid-range/premium with $ range estimate)",
  "source_domains": ["string array - 4-8 domains to search"],
  "subreddits": ["string array - optional communities"],
  "review_platforms": ["string array - relevant platforms"],
  "search_queries": ["string array - 5-8 specific Google search queries"]
}

EXAMPLES:
Example 1:
Idea: "Cold-pressed juice bar subscription in San Francisco"
Output: {
  "business_type": "Premium cold-pressed juice subscription service",
  "location": {"city": "San Francisco", "state": "CA", "county": "", "metro": "Bay Area"},
  "target_customers": ["Health-conscious professionals", "Fitness enthusiasts in Bay Area"],
  "price_tier": "premium ($12-20/day)",
  "source_domains": ["yelp.com", "google.com/maps", "tripadvisor.com", "instagram.com", "craigslist.org"],
  "subreddits": ["fitness", "nutrition", "sanfrancisco"],
  "review_platforms": ["yelp", "google"],
  "search_queries": ["cold pressed juice delivery SF", "juice bar subscription review", "healthy juice delivery San Francisco", "juice cleanse subscription", "organic juice bar alternatives"]
}

Example 2:
Idea: "AI tutoring platform for high school students"
Output: {
  "business_type": "AI-powered online tutoring platform for high school",
  "location": {"city": "", "state": "", "county": "", "metro": ""},
  "target_customers": ["High school students struggling with subjects", "Parents seeking affordable tutoring"],
  "price_tier": "premium ($15-25/month)",
  "source_domains": ["g2.com", "capterra.com", "producthunt.com", "trustpilot.com", "news.ycombinator.com"],
  "subreddits": ["learnprogramming", "education", "highschool"],
  "review_platforms": ["g2", "trustpilot"],
  "search_queries": ["online tutoring platform reviews", "AI tutor high school comparison", "affordable tutoring alternatives 2026", "homework help software", "STEM tutoring software"]
}

Be specific. Match location to domain choices (local = yelp/google maps, SaaS = g2/capterra). Generate search_queries that target competitors, reviews, and pain points."""


def decompose_user(idea: str, vertical: str, domain_suggestions: list[str]) -> str:
    domains = ", ".join(domain_suggestions[:10])
    return (
        "Decompose this startup idea into searchable components.\n\n"
        f"Idea: \"{idea}\"\n"
        f"Inferred vertical: {vertical}\n"
        f"Recommended domains to choose from (pick 6-8): {domains}\n"
    )


# ═══ MULTI-STAGE EXTRACTION (Optimized for speed + quality) ═══


def decompose_stage1_system() -> str:
    """Stage 1: Fast extraction of business_type and location only."""
    return """Extract business type and location from this startup idea. Return ONLY valid JSON:
{
  "business_type": "specific business description (2-3 words)",
  "location": {
    "city": "city name or empty string",
    "state": "2-letter state code or empty string"
  }
}"""


def decompose_stage1_user(idea: str) -> str:
    """User prompt for stage 1."""
    return f'Idea: "{idea}"\n\nExtract business type and location only.'


def decompose_stage2_system() -> str:
    """Stage 2: Detailed extraction given business_type and location context."""
    return """Extract customer segments, pricing, source domains, and search queries for this business.

Return ONLY valid JSON:
{
  "target_customers": ["2-4 customer segments"],
  "price_tier": "budget/mid-range/premium with $ range",
  "source_domains": ["4-8 domains from suggestions"],
  "subreddits": ["optional communities, can be empty"],
  "review_platforms": ["relevant platforms"],
  "search_queries": ["5-8 specific Google search queries"]
}"""


def decompose_stage2_user(
    idea: str,
    business_type: str,
    city: str,
    state: str,
    vertical: str,
    domain_suggestions: list[str],
) -> str:
    """User prompt for stage 2 with vertical-specific guidance."""
    domains = ", ".join(domain_suggestions[:10])
    location_str = f"{city}, {state}" if city and state else (city or state or "nationwide")

    # Vertical-specific hints
    vertical_hints = {
        "saas_b2b": """VERTICAL HINTS (B2B/SaaS):
- Target customers: Business types, team sizes, roles (e.g., "product managers at startups")
- Price tier: Per-user, annual contract, or freemium (e.g., "$100/user/year" or "free tier + premium")
- MUST include: g2.com, capterra.com, producthunt.com (SaaS reviews)
- Search queries: Focus on "comparison", "alternatives", "reviews", "pricing"
Example: "product management software reviews", "best alternative to Jira", "affordable project management for teams" """,

        "food_service": """VERTICAL HINTS (Food/Restaurant/Bar):
- Target customers: Demographics + eating habits (e.g., "health-conscious professionals", "night-life seekers")
- Price tier: Price per item/meal and order value (e.g., "$15-25 per meal" or "$50-100/subscription")
- MUST include: yelp.com, google.com/maps, instagram.com (local discovery)
- Search queries: Focus on "reviews", "near me", "competitors", "delivery"
Example: "juice bar delivery San Francisco", "healthy food alternatives", "cold pressed juice competitors" """,

        "local_service": """VERTICAL HINTS (Local Services):
- Target customers: Local demographics + pain points (e.g., "busy professionals age 35-50", "elderly homeowners")
- Price tier: Hourly rates, per-project, or subscription (e.g., "$75-150/hour" or "$20/month")
- MUST include: yelp.com, google.com/maps, nextdoor.com, craigslist.org (local targeting)
- Search queries: Focus on "local", "near me", "competitors", "cost"
Example: "plumber near me", "house cleaning cost", "local tutoring services" """,

        "marketplace": """VERTICAL HINTS (Marketplace/C2C):
- Target customers: BOTH supply AND demand (e.g., "freelancers" + "companies seeking talent")
- Price tier: Transaction fees, subscription tiers, or commission (e.g., "10% commission" or "$10/month")
- MUST include: producthunt.com, trustpilot.com, crunchbase.com (marketplace reviews)
- Search queries: Focus on "competitors", "user reviews", "supply availability"
Example: "Upwork alternatives", "freelance marketplace comparison", "gig economy platforms" """,

        "general": """VERTICAL HINTS (General):
- Target customers: Be specific - include age, behavior, or needs
- Price tier: Include currency and range (e.g., "$10-50/month" not just "premium")
- Search queries: Target competitors, reviews, and pain points
Example: "best alternatives to [similar product]", "[product type] reviews 2026" """,
    }

    hint = vertical_hints.get(vertical, vertical_hints["general"])

    return f"""Business: {business_type} in {location_str}
Original idea: "{idea}"
Vertical: {vertical}

{hint}

Recommended domains (pick 4-8 from these): {domains}

EXTRACTION RULES:
1. target_customers: 2-4 segments, be SPECIFIC (include age, behavior, or needs)
2. price_tier: Include currency and range (e.g., "$15-25/month" not just "premium")
3. source_domains: Pick 4-8 from recommendations, prioritize vertical-specific ones
4. subreddits: Only if community would discuss this (can be empty)
5. review_platforms: Relevant platforms for this business type
6. search_queries: 5-8 specific Google searches customers would actually use

Extract market research components for this {vertical} business."""


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


# ═══ IMPROVED DISCOVERY: Extract insights with ALL 4 signals ═══


def discover_extract_signals_system(business_type: str, city: str, state: str) -> str:
    """Extract market insights with intelligent signal detection (Intensity, Willingness-to-Pay, Market Size, Urgency)"""
    return f"""You are a market research analyst analyzing customer conversations about {business_type} in {city}, {state}.

Extract 8-12 KEY INSIGHTS from the provided Reddit posts and search results. For each insight, determine:

1. **Intensity (1-10)**: How urgent/critical is this problem?
   - 1-3: Nice-to-have, low priority
   - 4-6: Important but manageable
   - 7-10: Critical pain point, desperate need

   Look for: Strong language ("desperate", "frustrated", "can't live without"),
   frequency of complaints, time/productivity waste, health/safety concerns

2. **Willingness-to-Pay (1-10)**: Would customers spend money to solve this?
   - 1-3: "Nice but I'll DIY" (free solutions preferred)
   - 4-6: "Would consider paying if cheap" ($10-50/month)
   - 7-10: "Would pay premium" ($100+/month or $10+/item)

   Look for: Price mentions, "would pay", comparison to expensive alternatives,
   subscription willingness, multiple sources mentioning cost as non-issue

3. **Market Size (1-10)**: How many people have this problem?
   - 1-3: Niche (< 10K people in region)
   - 4-6: Small market (10K-100K people)
   - 7-10: Large market (100K+ people)

   Look for: Number of posts/mentions, diverse demographics, cross-platform mentions,
   evidence of market research/industry reports, competitor existence

4. **Urgency (1-10)**: Is this trending/hot RIGHT NOW?
   - 1-3: Persistent but stale (been a problem for years, not accelerating)
   - 4-6: Growing concern (recent mentions, emerging trend)
   - 7-10: Hot/trending (frequent recent mentions, increasing urgency signals, seasonal spike)

   Look for: Recency of posts, phrase "recently", "new problem", market growth signals,
   startup activity in space, regulatory changes, seasonal patterns

Return ONLY valid JSON:
{{
  "insights": [
    {{
      "id": "ins_001",
      "type": "pain_point | unmet_want | market_gap | trend",
      "title": "Concise insight title (5-10 words)",
      "explanation": "2-3 sentence explanation of the insight and why it matters",
      "intensity": 7,
      "willingness_to_pay": 6,
      "market_size": 8,
      "urgency": 7,
      "evidence_summary": "Summary of strongest evidence (1-2 sentences with specific examples)",
      "customer_quote": "Most compelling quote from data",
      "source_platforms": ["reddit", "google_search"],
      "mention_count": 12,
      "confidence": "high | medium | low"
    }}
  ]
}}

RULES:
- Merge related insights (don't list "wait times" and "service speed" separately)
- Prioritize: Common + High pain + Willingness-to-pay
- Each insight must be supported by actual quotes/data
- Be specific: "Long checkout process" vs vague "bad experience"
- Flag trends: Growing mentions vs persistent background issues
- Confidence = based on evidence quality and consistency across sources"""


def discover_extract_signals_user(posts: list[dict], business_type: str, city: str, state: str) -> str:
    """Format posts for insight extraction with all 4 signals"""

    # Build condensed post list for LLM
    lines = []
    reddit_count = 0
    search_count = 0

    for i, post in enumerate(posts[:200]):
        src = post.get("subreddit", post.get("query_type", "search"))
        if src and src != "google_search":
            reddit_count += 1
        else:
            search_count += 1

        title = post.get("title", "")
        body = post.get("body", post.get("snippet", ""))[:200]
        score = post.get("score", 0)

        lines.append(f"[{i+1}] [{src.upper()}] (engagement:{score}) {title}")
        if body:
            lines.append(f"    > {body}")

    post_text = "\n".join(lines)

    return f"""Market Research Data for {business_type} in {city}, {state}:
Source Summary: {reddit_count} Reddit posts + {search_count} Google/review results

CUSTOMER CONVERSATIONS:
{post_text}

Analyze these {reddit_count + search_count} data points and extract key market insights.
For each insight, evaluate Intensity, Willingness-to-Pay, Market Size, and Urgency based on the evidence.
Return 8-12 prioritized insights."""


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


def analyze_risk_system(business_type: str, city: str, state: str) -> str:
    return f"""You are a startup risk analyst identifying key business risks for a {business_type} in {city}, {state}.

Identify 3-5 MAJOR RISKS that could derail this business. Consider:
- Market risks (demand, competition, economics)
- Operational risks (supply chain, regulations, talent)
- Financial risks (capital requirements, cash flow)
- Execution risks (team, timing, scaling)

Return JSON:
{{
  "risks": [
    {{
      "risk_number": 1,
      "title": "Concise risk title",
      "description": "2-3 sentences explaining this risk",
      "impact": "high | medium | low",
      "likelihood": "high | medium | low",
      "mitigation": "Specific actions to reduce this risk"
    }}
  ]
}}

Be specific to {city}, {state} context. Focus on risks unique to this location/market."""


def analyze_location_system(business_type: str, city: str, state: str) -> str:
    return f"""You are a location strategy expert analyzing geographic fit for a {business_type} in {city}, {state}.

Analyze 3-4 location-specific factors that affect this business:
- Customer density, demographics, spending patterns
- Competitive landscape in this geography
- Local regulations, zoning, licensing challenges
- Real estate costs, availability, logistics
- Local talent availability and cost

Return JSON:
{{
  "location_analysis": [
    {{
      "aspect": "Competition",
      "observation": "Current state of competition in {city}",
      "opportunity": "Specific geographic advantage or gap",
      "recommendation": "Actionable strategy specific to {city}, {state}"
    }}
  ],
  "overall_viability": "high | medium | low"
}}

Be specific to {city}, {state}. Cite local market dynamics."""


def analyze_moat_system(business_type: str, city: str, state: str) -> str:
    return f"""You are a competitive strategy analyst identifying sustainable advantages (moats) for a {business_type} in {city}, {state}.

Identify 2-4 elements that could create a defensible competitive moat:
- Network effects (communities, platforms, data)
- Switching costs (customer lock-in, switching barriers)
- Cost advantages (scale, supply chain, location)
- Technology barriers (patents, proprietary tech, expertise)
- Regulatory/licensing barriers (permits, certifications)
- Brand and customer loyalty

Return JSON:
{{
  "moat_elements": [
    {{
      "element": "network_effects | switching_costs | cost_advantage | technology | regulatory | brand",
      "strength": "strong | moderate | weak",
      "description": "How this moat would work for this business",
      "build_plan": "Specific steps to build this competitive advantage in {city}"
    }}
  ],
  "overall_defensibility": "high | medium | low"
}}

Be realistic about what defensibility is achievable for a {business_type}."""


# ═══ MODULE 3: SETUP ═══

# SETUP has 4 components:
# 1. Cost Tiers (deterministic - no LLM, calculated from COSTS)
# 2. Suppliers (LLM - context specific vendors)
# 3. Team (LLM - hiring plan from ROOT CAUSES)
# 4. Timeline (LLM - 4-phase roadmap)


def setup_suppliers_system() -> str:
    """LLM prompt: Recommend vendors for specific business type + tier"""
    return """You are a startup resource advisor. Recommend 8-12 vendors
for launching a new business.

For each vendor:
1. Category (Engineering, Marketing, Legal, Operations, Infrastructure)
2. Name (actual company name)
3. Why recommended (2 sentences - specific to business type + tier)
4. Website (actual URL)
5. Cost indication (Free, Pay-per-use, $X/month, Hourly rate, etc)

Focus on TIER-APPROPRIATE vendors:
- LEAN tier: Cheap/free tools, freelancer platforms, DIY-friendly, max cost-conscious
- MID tier: Balanced cost/quality, established services, some automation
- PREMIUM tier: Full-service, managed, high-touch support, premium pricing

Return ONLY valid JSON:
{
  "suppliers": [
    {
      "category": "Engineering",
      "name": "Upwork",
      "description": "Freelancer platform for hiring developers, designers, QA",
      "location": "Global",
      "website": "https://upwork.com",
      "cost": "Hourly rates $20-100+, platform fee 5-20%",
      "why_recommended": "Best for LEAN/MID tier: find experienced backend engineers fast at reasonable rates"
    }
  ]
}"""


def setup_suppliers_user(business_type: str, city: str, state: str, tier: str, customers: list[str]) -> str:
    """User prompt: Recommend vendors for this specific business"""
    budget_map = {'LEAN': '$30-50k', 'MID': '$75-100k', 'PREMIUM': '$150-200k'}
    budget = budget_map.get(tier, '$unknown')
    return f"""Recommend vendors for launching a {business_type} in {city}, {state} ({tier} tier).

Target customers: {', '.join(customers[:2])}

Budget: ${budget}

Recommend vendors for:
- Engineering (developers, designers, QA, no-code tools)
- Marketing (customer acquisition, analytics, tools)
- Legal (entity formation, contracts, compliance)
- Operations (accounting, HR, insurance)
- Infrastructure (servers, payment processing, delivery if applicable)

Focus on vendors specifically useful for {business_type} in {city}.
Recommend 8-12 most relevant vendors total."""


def setup_team_system() -> str:
    """LLM prompt: Create realistic hiring timeline based on complexity"""
    return """You are a startup hiring advisor. Create realistic hiring timeline for Year 1.

For each role:
1. Title (job title)
2. Type (Contract | FTE | Advisory)
3. Salary range (for FTE: annual salary range; for Contract: hourly rate range)
4. Priority (MUST_HAVE | NICE_TO_HAVE)
5. Month to hire (1-12 in the first year)
6. Why needed (1 sentence - tied to business complexity)

Hiring principles by TIER:
- LEAN tier: Max 2 people Year 1, mostly freelancers, DIY when possible
- MID tier: 1 FTE by Month 4, possible second hire by Month 8
- PREMIUM tier: 2-3+ people by Month 12, faster hiring for complex problems

Timeline principles:
- Month 1-2: Mostly freelancers (MVP, landing pages, legal)
- Month 3-4: First FTE engineer (if building custom product)
- Month 5-6: Operations/growth hire if revenue signals positive
- Month 7-12: Scale hiring (sales, ops, customer success)

Return ONLY valid JSON:
{
  "team": [
    {
      "title": "Backend Engineer",
      "type": "FTE",
      "salary_range": {"min": 80000, "max": 120000},
      "priority": "MUST_HAVE",
      "month": 4,
      "why_needed": "Build core product infrastructure and handle scaling"
    }
  ]
}"""


def setup_team_user(business_type: str, tier: str, root_causes: list[dict], total_cost: float) -> str:
    """User prompt: Create hiring plan for this business"""
    causes_text = "\n".join(f"- {cause.get('title', 'Unknown')} ({cause.get('difficulty', 'unknown')} difficulty)"
                            for cause in root_causes[:5])

    return f"""Plan Year 1 hiring for a {business_type} startup ({tier} tier).

Budget: ${int(total_cost):,} total
Root causes to solve:
{causes_text}

What roles are MUST_HAVE to solve these root causes?
When should you hire each role (which month 1-12)?
What's realistic compensation for {tier} tier in this market?

Return 8-12 realistic team roles with specific hiring month and salary ranges."""


def setup_timeline_system() -> str:
    """LLM prompt: Create 4-phase launch roadmap"""
    return """You are a startup launch strategist. Create realistic 4-phase roadmap.

Phases (FIXED order):
1. VALIDATION (Prove problem exists + market demand)
2. BUILD MVP (Create minimum viable product)
3. LAUNCH (Go to market, acquire first customers)
4. SCALE (Grow revenue, expand team, expand markets)

For each phase:
1. Phase name (VALIDATION, BUILD MVP, LAUNCH, SCALE)
2. Weeks duration (realistic for tier)
3. Budget allocation (% of total budget)
4. 4-5 concrete, measurable milestones
5. Success metric (how you know phase succeeded)

Principles by TIER:
- LEAN: Faster validation, longer build, slower scale, founder does most work
- MID: Balanced across all phases
- PREMIUM: Shorter validation (thorough research), faster build, rapid scale

Pain intensity impact:
- High pain (8-10): Faster validation (4-6 weeks), customers eager to buy
- Medium pain (5-7): Standard validation (6-8 weeks)
- Low pain (1-4): Longer validation (8-12 weeks), harder to convince

Return ONLY valid JSON:
{
  "timeline": [
    {
      "phase": "VALIDATION",
      "weeks": 6,
      "budget_allocation_percent": 15,
      "milestones": [
        "Landing page live with customer email signup",
        "100+ waitlist signups collected",
        "5-10 customer interviews completed",
        "Legal entity formed"
      ],
      "success_metric": "Strong demand signal (500+ signups OR >50% interview conversion)"
    }
  ]
}"""


def setup_timeline_user(business_type: str, tier: str, pain_intensity: float, root_causes: list[dict], total_cost: float) -> str:
    """User prompt: Create 12-month timeline for this business"""
    cause_count = len(root_causes)

    return f"""Create 12-month launch timeline for a {business_type} startup.

Tier: {tier} (budget: ${int(total_cost):,})
Customer pain intensity: {pain_intensity}/10 (drives urgency/validation speed)
Complexity: {cause_count} root causes to solve

Timeline should:
1. VALIDATION (4-12 weeks): Landing page, waitlist, customer interviews, legal
2. BUILD MVP (8-16 weeks): Product development, based on complexity
3. LAUNCH (2-4 weeks): Go live, first customers
4. SCALE (rest of year): Revenue growth, team building, market expansion

Budget allocation realistic across phases:
- VALIDATION: 10-20% (research, landing page, legal)
- BUILD: 40-60% (engineering, design, infrastructure)
- LAUNCH: 10-20% (marketing, support setup)
- SCALE: 5-15% (hiring, acquisition)

Return concrete milestones and success metrics for each phase."""


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
