# SETUP Tab: Data Sources, LLM Prompts & Caching

## Data Flow Architecture

```
ANALYZE Outputs (from prior sections)
├─ ROOT CAUSES [3-5 items with difficulty: easy|medium|hard]
├─ COSTS [total_range + breakdown by category]
├─ CUSTOMERS [3-4 segments with pain_intensity + location]
├─ OPPORTUNITY [SAM, SOM]
└─ DECOMPOSE [business_type, location, target_customers]

        ↓↓↓ (SETUP processes) ↓↓↓

SETUP Outputs
├─ Cost Tiers [3 models: LEAN/MID/PREMIUM with ranges]
├─ Suppliers [vendors per category, specific to business type + location]
├─ Team [roles + timeline + salary ranges]
└─ Timeline [4 phases with milestones + cost allocation]
```

---

## Component 1: COST TIERS

### Data Sources

**Input from COSTS section:**
```python
costs = {
    "total_range": {
        "min": 50000,
        "max": 100000
    },
    "breakdown": [
        {"category": "Engineering", "range": {"min": 20000, "max": 40000}},
        {"category": "Operations", "range": {"min": 5000, "max": 10000}},
        {"category": "Marketing", "range": {"min": 15000, "max": 30000}},
        {"category": "Infrastructure", "range": {"min": 5000, "max": 15000}},
        {"category": "Working Capital", "range": {"min": 5000, "max": 5000}}
    ]
}
```

**Hardcoded multipliers (no LLM needed - deterministic):**
```python
TIER_MULTIPLIERS = {
    "LEAN": {
        "min_multiplier": 0.6,      # 60% of baseline min
        "max_multiplier": 0.8,      # 80% of baseline min
        "philosophy": "Speed + founder effort, no external hires",
        "approach": "No-code tools, freelancers, DIY",
        "team_size": 1,
        "timeline_weeks": 16  # 4 months
    },
    "MID": {
        "min_multiplier": 1.0,      # 100% = baseline
        "max_multiplier": 1.0,      # 100% = baseline
        "philosophy": "Balanced speed, quality, team",
        "approach": "Custom app, 1 FTE engineer",
        "team_size": 1-2,
        "timeline_weeks": 24  # 6 months
    },
    "PREMIUM": {
        "min_multiplier": 1.2,      # 120% of baseline max
        "max_multiplier": 1.8,      # 180% of baseline max
        "philosophy": "Quality + team, higher burn",
        "approach": "Custom + team, multiple hires",
        "team_size": 2-3,
        "timeline_weeks": 32  # 8 months
    }
}
```

### LLM Prompt: NOT NEEDED (Deterministic)

**Why:** Cost tier calculation is pure math, no LLM:
```python
def generate_cost_tiers(costs):
    """Generate 3 tiers from COSTS data - NO LLM CALL"""

    tiers = []
    for tier_name, multipliers in TIER_MULTIPLIERS.items():
        min_cost = int(costs["total_range"]["min"] * multipliers["min_multiplier"])
        max_cost = int(costs["total_range"]["max"] * multipliers["max_multiplier"])

        tiers.append({
            "tier": tier_name,
            "model": tier_name,
            "total_range": {
                "min": min_cost,
                "max": max_cost,
                "formatted": f"${min_cost/1000:.0f}k - ${max_cost/1000:.0f}k"
            },
            "philosophy": multipliers["philosophy"],
            "approach": multipliers["approach"],
            "team_size": multipliers["team_size"],
            "timeline_weeks": multipliers["timeline_weeks"],
            "line_items": breakdown_by_tier(costs["breakdown"], tier_name)
        })

    return tiers
```

### Caching Strategy

**Cache Key:**
```
setup:cost_tiers:{business_type}|{city}|{state}
```

**TTL:** 30 days (cost estimates don't change often)

**Cache Trigger:**
- Generate once COSTS section complete
- Store immediately after generation (deterministic output)

**Invalidation:**
- If COSTS section updated → invalidate

```python
async def cache_cost_tiers(business_type, city, state, tiers):
    """Store cost tiers in database for 30 days"""
    await db.insert("""
        INSERT INTO setup_cache (cache_key, data, expires_at)
        VALUES ($1, $2, NOW() + INTERVAL '30 days')
        ON CONFLICT (cache_key)
        DO UPDATE SET data = $2, expires_at = NOW() + INTERVAL '30 days'
    """, [
        f"setup:cost_tiers:{business_type}|{city}|{state}",
        json.dumps(tiers)
    ])
```

---

## Component 2: SUPPLIERS

### Data Sources

**Input:**
```python
sources = {
    "business_type": "cold-pressed juice subscription",
    "location": {"city": "San Francisco", "state": "CA"},
    "target_customers": ["Health-conscious professionals", "Fitness enthusiasts"],
    "selected_tier": "MID"  # User selected tier
}
```

### LLM Prompt: NEEDED (Context-Specific)

**Why:** Different businesses need different suppliers (SaaS vs Food Service vs Local Service)

**System Prompt:**
```python
def setup_suppliers_system() -> str:
    return """You are a startup resource advisor. Recommend 6-10 vendors
for specific business categories.

For each vendor:
1. Category (Engineering, Marketing, Legal, Operations, Infrastructure)
2. Name (actual company name)
3. Why recommended (2 sentences - specific to business type + tier)
4. Website (actual URL)
5. Cost indication (Free, Pay-per-use, $X/month, Hourly rate)

Focus on TIER-APPROPRIATE vendors:
- LEAN tier: Cheap/free tools, freelancer platforms, DIY-friendly
- MID tier: Balanced cost/quality, established services, some automation
- PREMIUM tier: Full-service, managed, high-touch support

Return JSON:
{
    "suppliers": [
        {
            "category": "Engineering",
            "name": "Upwork",
            "why_recommended": "For MID tier: find experienced backend engineers at $40-60/hr",
            "website": "https://upwork.com",
            "cost": "Hourly rates $20-100+, platform fee 5-20%"
        }
    ]
}"""
```

**User Prompt:**
```python
def setup_suppliers_user(business_type, city, state, tier, customers) -> str:
    return f"""Recommend vendors for this startup's launch ({tier} tier):

Business: {business_type}
Location: {city}, {state}
Target Customers: {', '.join(customers[:2])}
Tier: {tier} (budget = ${'30-50k' if tier=='LEAN' else ('75-100k' if tier=='MID' else '150-200k')})

Recommend vendors for:
- Engineering (developers, designers, QA)
- Marketing (customer acquisition, tools)
- Legal (entity formation, contracts)
- Operations (accounting, HR, insurance)
- Infrastructure (servers, payment, delivery/logistics)

Focus on vendors specifically useful for {business_type} in {city}.
Return 8-12 most relevant vendors."""
```

### Caching Strategy

**Cache Key:**
```
setup:suppliers:{business_type}|{city}|{state}|{tier}
```

**TTL:** 60 days (vendor recommendations stable)

**Cache Trigger:**
- Generate after tier selected
- LLM call → cache result

**Invalidation:**
- If business_type changes → invalidate all tiers

```python
async def cache_suppliers(business_type, city, state, tier, suppliers):
    """Store suppliers in database for 60 days"""
    await db.insert("""
        INSERT INTO setup_cache (cache_key, data, expires_at)
        VALUES ($1, $2, NOW() + INTERVAL '60 days')
        ON CONFLICT (cache_key)
        DO UPDATE SET data = $2
    """, [
        f"setup:suppliers:{business_type}|{city}|{state}|{tier}",
        json.dumps(suppliers)
    ])
```

---

## Component 3: TEAM

### Data Sources

**Input from ROOT CAUSES + Tier Selection:**
```python
sources = {
    "root_causes": [
        {"title": "Wait times", "difficulty": "easy"},
        {"title": "Supply chain", "difficulty": "medium"},
        {"title": "Pricing gap", "difficulty": "hard"}
    ],
    "selected_tier": "MID",
    "costs": {"total_range": {"min": 75000, "max": 100000}},
    "business_type": "cold-pressed juice"
}
```

### LLM Prompt: NEEDED (Complexity-Dependent)

**Why:** Team needs depend on ROOT CAUSES difficulty + tier choice

**System Prompt:**
```python
def setup_team_system() -> str:
    return """You are a startup hiring advisor. Create realistic hiring timeline.

For each role:
1. Title (job title)
2. Type (Contract | FTE | Advisory)
3. Salary range (for FTE: annual; for Contract: hourly)
4. Priority (MUST_HAVE | NICE_TO_HAVE)
5. Month to hire (1-12 in the first year)
6. Why needed (1 sentence - linked to ROOT CAUSE)

Hiring principles:
- Month 1-2: Mostly freelancers (MVPs, landing pages, legal)
- Month 3-4: First FTE engineer (if building custom MVP)
- Month 5-6: Operations/growth if revenue signals
- Month 7-12: Scale hiring (sales, ops, marketing)

LEAN tier: Max 2 people Year 1
MID tier: 1 FTE by Month 4, possible second hire by Month 8
PREMIUM tier: 2-3 people by Month 12

Return JSON:
{
    "team": [
        {
            "title": "Backend Engineer",
            "type": "FTE",
            "salary_range": {"min": 80000, "max": 120000},
            "priority": "MUST_HAVE",
            "month": 4,
            "why_needed": "Solve ROOT CAUSE #2: Build cold-chain logistics integration"
        }
    ]
}"""
```

**User Prompt:**
```python
def setup_team_user(root_causes, tier, costs, business_type) -> str:
    return f"""Plan Year 1 hiring for {business_type} startup.

Tier: {tier} (budget: $X total)
Root causes to solve:
{chr(10).join(f'- {cause["title"]} ({cause["difficulty"]})' for cause in root_causes)}

What roles are MUST_HAVE to solve these causes?
When should you hire (by which month)?
What's realistic compensation for {tier} tier?

Return 8-12 realistic team roles with hiring timeline."""
```

### Caching Strategy

**Cache Key:**
```
setup:team:{business_type}|{tier}
```

**TTL:** 30 days (hiring plans change with market conditions)

**Cache Trigger:**
- Generate after tier selected and ROOT CAUSES available
- LLM call → cache

**Invalidation:**
- If ROOT CAUSES changed → invalidate
- If tier changed → invalidate

```python
async def cache_team(business_type, tier, team_plan):
    """Store team plan in database for 30 days"""
    await db.insert("""
        INSERT INTO setup_cache (cache_key, data, expires_at)
        VALUES ($1, $2, NOW() + INTERVAL '30 days')
        ON CONFLICT (cache_key)
        DO UPDATE SET data = $2, expires_at = NOW() + INTERVAL '30 days'
    """, [
        f"setup:team:{business_type}|{tier}",
        json.dumps(team_plan)
    ])
```

---

## Component 4: TIMELINE

### Data Sources

**Input:**
```python
sources = {
    "selected_tier": "MID",
    "costs": {"total_range": {"min": 75000, "max": 100000}},
    "customers": [
        {"name": "Health-conscious professionals", "pain_intensity": 8},
        {"name": "Fitness enthusiasts", "pain_intensity": 7}
    ],
    "root_causes": [
        {"title": "Wait times", "difficulty": "easy"},
        {"title": "Supply chain", "difficulty": "medium"}
    ]
}
```

### LLM Prompt: NEEDED (Phase Planning)

**Why:** Timeline depends on complexity, budget, customer pain intensity

**System Prompt:**
```python
def setup_timeline_system() -> str:
    return """You are a startup launch strategist. Create realistic 4-phase roadmap.

Phases (fixed):
1. VALIDATION (Prove problem + demand)
2. BUILD MVP (Create minimum viable product)
3. LAUNCH (Go public, acquire first customers)
4. SCALE (Grow revenue, expand team)

For each phase:
1. Weeks duration (how long realistically)
2. Budget allocation (% of total)
3. 4-5 concrete milestones (measurable outcomes)
4. Success metric (how you know it worked)

Principles:
- LEAN tier: Faster validation, longer build, slower scale
- MID tier: Balanced across all phases
- PREMIUM tier: Slower validation (thorough), faster build, rapid scale
- Higher pain intensity → faster validation → more customer urgency

Return JSON:
{
    "timeline": [
        {
            "phase": "VALIDATION",
            "weeks": 6,
            "budget_allocation_percent": 15,
            "milestones": [
                "Landing page live",
                "100 waitlist signups",
                "5 user interviews",
                "Legal entity formed"
            ],
            "success_metric": "Strong demand signal (>500 signups OR high NPS)"
        }
    ]
}"""
```

**User Prompt:**
```python
def setup_timeline_user(tier, root_causes, customers, total_cost) -> str:
    max_pain = max(c.get("pain_intensity", 5) for c in customers) if customers else 5

    return f"""Create 12-month launch timeline for {tier} tier startup.

Key constraints:
- Budget: ${total_cost/1000:.0f}k
- Customer pain intensity: {max_pain}/10 (drives urgency)
- Complexity: {len(root_causes)} root causes to solve

Timeline should:
1. Start with VALIDATION (landing page, waitlist, research) - 4-8 weeks
2. Move to BUILD MVP (engineering-heavy) - 8-12 weeks
3. Launch to early customers - 2-4 weeks
4. Scale and grow - remaining months

Allocate budget realistically:
- VALIDATION: 10-20% (research, landing page, legal)
- BUILD: 40-60% (engineering, design, infra)
- LAUNCH: 10-20% (marketing, customer support setup)
- SCALE: 5-15% (hiring, customer acquisition)

Return concrete milestones for each phase."""
```

### Caching Strategy

**Cache Key:**
```
setup:timeline:{business_type}|{tier}|{pain_level}
```

**TTL:** 30 days (plans updated as reality changes)

**Cache Trigger:**
- Generate after tier + root_causes available
- LLM call → cache

**Invalidation:**
- If ROOT CAUSES changed → invalidate
- If CUSTOMERS pain_intensity changed significantly → invalidate
- If tier changed → invalidate

```python
async def cache_timeline(business_type, tier, pain_level, timeline):
    """Store timeline in database for 30 days"""
    await db.insert("""
        INSERT INTO setup_cache (cache_key, data, expires_at)
        VALUES ($1, $2, NOW() + INTERVAL '30 days')
        ON CONFLICT (cache_key)
        DO UPDATE SET data = $2, expires_at = NOW() + INTERVAL '30 days'
    """, [
        f"setup:timeline:{business_type}|{tier}|{pain_level}",
        json.dumps(timeline)
    ])
```

---

## Implementation: Cache Table

**Create SQL table (if not exists):**

```sql
CREATE TABLE IF NOT EXISTS setup_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    -- cache_key format: "setup:{component}:{business_type}|{city}|{state}|{tier}"
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    hit_count INT DEFAULT 0
);

CREATE INDEX idx_setup_cache_key ON setup_cache(cache_key);
CREATE INDEX idx_setup_cache_expires ON setup_cache(expires_at);
```

---

## API Endpoint: POST /api/setup

```python
@router.post("/api/setup", response_model=SetupResponse)
async def setup_section(req: SetupRequest) -> SetupResponse:
    """Generate complete launch plan from ANALYZE data"""

    decomp = req.decomposition.model_dump()
    business_type = decomp.get("business_type", "")
    location = decomp.get("location", {})
    city = location.get("city", "")
    state = location.get("state", "")
    tier = req.selected_tier  # "LEAN" | "MID" | "PREMIUM"

    # Check cache before generating
    cache_hit = await check_setup_cache(business_type, city, state, tier)
    if cache_hit:
        logger.info(f"Setup cache hit: {business_type} {city} {tier}")
        return cache_hit

    # 1. COST TIERS (deterministic, no LLM)
    cost_tiers = generate_cost_tiers(req.prior_context["costs"])

    # 2. SUPPLIERS (LLM + cache)
    suppliers = await get_or_generate_suppliers(
        business_type, city, state, tier,
        decomp.get("target_customers", [])
    )

    # 3. TEAM (LLM + cache)
    team = await get_or_generate_team(
        business_type, tier,
        req.prior_context.get("root_causes", []),
        req.prior_context.get("costs", {})
    )

    # 4. TIMELINE (LLM + cache)
    max_pain = max(
        seg.get("pain_intensity", 5)
        for seg in req.prior_context.get("customers", {}).get("segments", [])
    ) if req.prior_context.get("customers") else 5

    timeline = await get_or_generate_timeline(
        business_type, tier, max_pain,
        req.prior_context.get("root_causes", []),
        req.prior_context.get("costs", {})
    )

    response = SetupResponse(
        cost_tiers=cost_tiers,
        suppliers=suppliers,
        team=team,
        timeline=timeline
    )

    # Cache entire response
    await cache_full_setup(business_type, city, state, tier, response)

    return response
```

---

## Caching Summary

| Component | LLM? | Cache TTL | Cache Key | Invalidation |
|-----------|------|-----------|-----------|--------------|
| **Cost Tiers** | ❌ No | 30d | `business_type\|city\|state` | COSTS changed |
| **Suppliers** | ✅ Yes | 60d | `business_type\|city\|state\|tier` | business_type changed |
| **Team** | ✅ Yes | 30d | `business_type\|tier` | ROOT_CAUSES changed |
| **Timeline** | ✅ Yes | 30d | `business_type\|tier\|pain_level` | ROOT_CAUSES or pain changed |

**Total LLM Calls per SETUP generation:** 3 (Suppliers, Team, Timeline)
**Total cache hits possible:** 4 components × multiple previous queries
**Token usage:** ~2000 tokens total across 3 LLM calls

