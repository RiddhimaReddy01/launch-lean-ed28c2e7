# COSTS Tab: Limiting Factors, Data Sources & Prompts

## Current COSTS Section (What It Does)

```
Input:  DECOMPOSE (business_type, location, team context)
        └─→ LLM estimates 5 cost categories
            ├─ Engineering
            ├─ Operations
            ├─ Marketing & Launch
            ├─ Infrastructure & Payment
            └─ Working Capital

Output: {
  "total_range": {"min": 50000, "max": 100000},
  "breakdown": [category costs...]
}
```

---

## Problem: Why COSTS Tab Fails (Score 4.8/10)

### The Core Issue
**Hardcoded cost ranges ignore business specifics.**

```
Input:  "Cold-pressed juice subscription"
Output: "Engineering $20k-40k" (applies to SaaS OR food service equally)

Reality:
  - SaaS tutoring: $25k (no-code platform)
  - Food delivery: $200k (supply chain + logistics)
  → Same range output = useless
```

---

## What COSTS Actually Needs: Limiting Factors

### 1. **Team Size & Experience** (Missing)
```
If founder has [0 engineers, first time]:
  → Engineering = $50k-80k (outsource/agencies)

If founder has [2 engineers, shipped before]:
  → Engineering = $15k-25k (lean approach)

Current: Assumes "founder is unpaid" only (too simplistic)
```

### 2. **Go-to-Market Model** (Invisible)
```
If B2B SaaS (long sales cycles):
  → Marketing = $30k-50k (content, partnerships, CAC)
  → Ops = $10k (legal for contracts)

If B2C Marketplace (network effects):
  → Marketing = $50k-100k (user acquisition, incentives)
  → Ops = $5k (basic T&Cs)

If Local Service (geographic):
  → Marketing = $5k (local ads, Google/Yelp)
  → Ops = $15k (licensing, insurance, legal)

Current: One generic breakdown for all
```

### 3. **Burn Rate Not Calculated**
```
Example: $75k MVP + $10k/month burn

Founder needs to know: "How many months of runway?"
  $75k ÷ $10k/month = 7.5 months

Current: Shows $75k but not "you need $100k for 15 months"
```

### 4. **Unit Economics Not Linked**
```
OPPORTUNITY says: SOM = $12M (Year 1)
COSTS says: Engineering = $20k
Founder thinks: "If I capture 1%, that's $120k revenue"
Reality: If CAC = $50 and LTV = $100, margin = $50/customer
         $120k revenue ÷ 50 = 2400 customers
         2400 × $50 CAC = $120k marketing spend
         But COSTS said $15k marketing!

Current: COSTS divorced from OPPORTUNITY/CUSTOMERS
```

### 5. **Scaling Costs Hidden**
```
MVP phase: "Build product" = $50k
Scale phase: "Hire team" = $200k/year
Maintenance: "Keep running" = $20k/year

Current: Only shows MVP, not "you'll need $250k next year"
```

---

## Data Sources for COSTS Tab

### Source 1: DECOMPOSE
```
Input fields used:
  ✓ business_type
  ✓ location (affects ops costs: SF ≠ Austin)
  ✓ target_customers (B2B/B2C affects marketing)

Missing from DECOMPOSE:
  ✗ team_size (affects engineering cost)
  ✗ business_model (affects marketing structure)
  ✗ timeline (MVP in 3 months vs 12 months?)
```

### Source 2: ROOT CAUSES
```
Each ROOT CAUSE has "difficulty" (easy/medium/hard)

Should inform COSTS:
  - Easy causes = lower engineering cost
  - Hard causes = hire specialized talent = higher cost
  - "Your move" complexity = time/money tradeoff

Example:
  ROOT CAUSE 1: "Wait times" (easy) → Simple logistics = $20k
  ROOT CAUSE 3: "Premium positioning" (hard) → Complex pricing/analytics = $50k

Current: COSTS doesn't reference ROOT CAUSES difficulty
```

### Source 3: CUSTOMERS
```
Should inform marketing budget:

  CUSTOMERS says: "Find in r/fitness, gym communities"
  COSTS should calculate:
    - Sponsoring r/fitness: $2k/month
    - Gym partnerships: $1k/month × 10 gyms = $10k setup
    - Total: $30k marketing for Year 1

Current: COSTS assumes generic $15k-30k marketing
```

---

## LLM Prompts for COSTS

### Current System Prompt
```python
def analyze_costs_system(business_type: str, city: str) -> str:
    return f"""Estimate MVP costs for {business_type}.

Categories:
- Engineering (dev, design, QA)
- Operations (legal, accounting, insurance)
- Marketing (launch, acquisition)
- Infrastructure (servers, payment)
- Working Capital (inventory)

Return JSON with min/max ranges for each.
Assume founder is unpaid.
Validate: min < max."""
```

**Problem:** No business model context, no limiting factors

### Better Prompt (What We Need)
```python
def analyze_costs_system_improved(
    business_type: str,
    city: str,
    go_to_market: str,  # "saas_b2b" | "marketplace" | "local_service"
    team_size: int,      # 1=solo, 2=co-founder, 3+=team
    root_causes: list,   # difficulty levels from ROOT CAUSES
) -> str:
    return f"""
Estimate MVP + Year 1 costs for {business_type} in {city}.
Go-to-market model: {go_to_market}
Founder team: {team_size} people

LIMITING FACTORS:
1. Team: {team_size} founders (affects engineering cost)
   - 1 person: outsource/agencies required
   - 2 people: one eng + one ops
   - 3+: can hire staff

2. Complexity: Root causes require {{easy|medium|hard}} engineering

3. Market: {go_to_market} markets require different acquisition costs
   - SaaS: content + partnerships = $30-50k
   - Marketplace: incentives + community = $50-100k
   - Local: geo-targeted ads = $5-20k

Calculate:
- Engineering: based on team + complexity
- Operations: based on business model + geography
- Marketing: based on {go_to_market} + customer locations
- Infrastructure: based on scale (MVP vs Year 1)
- Working Capital: based on business model
- Monthly burn rate
- Runway months at current cost

Return JSON with:
{{
  "total_range": {{"min": X, "max": Y}},
  "monthly_burn": {{"min": X, "max": Y}},
  "runway_months": {{"min": X, "max": Y}},
  "breakdown": [
    {{
      "category": "Engineering",
      "rationale": "Based on {team_size} founders + {difficulty} complexity",
      "range": {{"min": X, "max": Y}},
      "items": "..."
    }}
  ]
}}"""
```

---

## Limiting Factors That Matter

### 1. **Team Size** (Biggest Cost Driver)
```
Solo founder + outsourcing: $80k (hire dev shop)
Co-founder pair (eng + ops): $40k (DIY)
Early team (3-5): $30k (cheap labor willing to take risk)
```

### 2. **Business Model Determines GTM Cost**
```
SaaS (long sales, high LTV): $40k marketing (build credibility)
Marketplace (network effects): $100k marketing (subsidize to attract)
Local Service (geo-targeted): $10k marketing (Google/Yelp ads)
E-commerce (direct): $50k marketing (Facebook/Google ads)
```

### 3. **Location** (Underestimated)
```
San Francisco: Everything 2x
  - Engineer hire: $150k/year (vs $80k elsewhere)
  - Office space: $3k/month
  - Permit/licensing: $2k

Austin/smaller city: 50% cheaper
  - Engineer hire: $80k/year
  - Office space: $1k/month
  - Permit/licensing: $500
```

### 4. **Complexity from ROOT CAUSES**
```
If ROOT CAUSES = ["wait times solved by app", "pricing tier", "email marketing"]
  → Simple = $30k engineering

If ROOT CAUSES = ["cold chain logistics", "supply chain partner", "ML recommendations"]
  → Complex = $150k engineering
```

### 5. **Burn Rate ÷ Runway**
```
Most critical for founder: "How long until we run out of money?"

$75k MVP cost
$10k/month burn (1 founder + AWS + marketing)
= 7.5 months before $0

Founder NEEDS to know: "Raise $100k min for 12 months, or get revenue"

Current: Shows $75k, hides the $10k/month cliff
```

---

## User POV: What Matters in COSTS

### What Founder Actually Needs
1. **"Can I bootstrap or need to raise?"**
   - If $30k total = yes, bootstrap
   - If $200k total = need angel/seed round

2. **"How long until we run out of money?"**
   - Burn rate + runway = survival clock

3. **"Where are costs going?"**
   - Engineering 40% vs Marketing 20% = prioritize engineering

4. **"Is this realistic?"**
   - "Compare to similar companies that succeeded"

### What Founder DOESN'T Need
- ❌ Detailed line-item justifications
- ❌ Cost optimization strategies
- ❌ Detailed hiring timelines
- ❌ Employee benefits breakdowns
- ❌ Historical cost benchmarks from unrelated companies

---

## Minimal Fix (User POV: Just Do This)

### Option 1: Keep COSTS as-is, Add 2 Fields
```json
{
  "total_range": {"min": 50000, "max": 100000, "formatted": "$50k-$100k"},
  "monthly_burn": {"min": 7500, "max": 12000, "formatted": "$7.5k-$12k/month"},
  "runway_months": {"min": 4, "max": 13, "formatted": "4-13 months before zero"},
  "breakdown": [...]
}
```

**Why:** Founder instantly sees "need 6-12 months funding"

### Option 2: Replace COSTS with GTM STRATEGY (Recommended)
```json
{
  "phases": [
    {
      "phase": 1,
      "name": "Validate & Launch",
      "duration": "3 months",
      "cost_range": {"min": 20000, "max": 50000},
      "activities": [
        "Landing page + email signup",
        "Community validation (r/fitness, etc)",
        "Pre-launch Reddit survey",
        "Email sequence for waitlist"
      ],
      "goal": "1000 waitlist signups"
    },
    {
      "phase": 2,
      "name": "MVP & First Customers",
      "duration": "3 months",
      "cost_range": {"min": 30000, "max": 60000},
      "activities": [
        "Build core product",
        "Beta with 50 users",
        "Refine based on feedback",
        "Prepare to scale"
      ],
      "goal": "$2k/month recurring revenue"
    },
    {
      "phase": 3,
      "name": "Growth & Scale",
      "duration": "6 months",
      "cost_range": {"min": 40000, "max": 100000},
      "activities": [
        "Hire 1 full-time engineer",
        "Paid acquisition (Facebook/Google/communities)",
        "Expand to 2-3 markets",
        "Optimize unit economics"
      ],
      "goal": "$10k/month recurring revenue"
    }
  ],
  "total_year_1_range": {"min": 90000, "max": 210000},
  "runway_needed": "12 months at $10k/month = $120k"
}
```

**Why:** Founder sees phases, funding milestones, and success metrics

---

## Implementation Decision

### For MVP/Demo (Do Minimal)
Keep COSTS as-is but:
1. Add `monthly_burn` calculation
2. Add `runway_months` display
3. Show "You need $XXk to survive 12 months"

**Time:** 30 mins to implement in discover.py

### For Quality Product (Do Right)
Replace COSTS with GO-TO-MARKET STRATEGY:
1. Extract business model from DECOMPOSE (B2B/B2C/Local/Marketplace)
2. Create 3-phase GTM plan
3. Show cost per phase + total runway

**Time:** 2 hours to implement

### For Later (Do Later)
Link to ROOT CAUSES difficulty:
1. Easy causes → lower engineering cost
2. Hard causes → higher engineering cost
3. Adjust breakdown based on actual ROOT CAUSES

**Time:** 1 hour later

---

## Summary: COSTS Tab

| Aspect | Current | Fix | Impact |
|--------|---------|-----|--------|
| **Data Source** | DECOMPOSE only | +ROOT CAUSES, +CUSTOMERS | Context-aware costs |
| **Limiting Factors** | Hidden | Show team size, GTM model, location | Founder understands tradeoffs |
| **Burn Rate** | Missing | Calculate monthly spend | Founder knows runway |
| **Runway** | Not shown | Display months before $0 | Survival clarity |
| **Complexity** | Generic ranges | Link to ROOT CAUSES difficulty | Realistic estimates |
| **Actionability** | Low (generic) | High (phased + milestones) | Founder can plan |

**User POV:** Just add runway months display. Everything else is optional.

