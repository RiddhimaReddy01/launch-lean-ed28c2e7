# ANALYZE Tab: Features & Intelligence

## Overview

The ANALYZE tab has **5 sections** that load on-demand (lazy-loaded when user clicks). Each section uses LLM + data ingestion to provide strategic insights.

```
USER SUBMITS IDEA
    ↓
DECOMPOSE (Tab 1) → extracts business_type, location, target_customers, pricing
    ↓
DISCOVER (Tab 1.5) → finds 10 market insights with evidence
    ↓
ANALYZE (Tab 2) → 5 strategic sections
    ├─→ [1] OPPORTUNITY (TAM/SAM/SOM market sizing)
    ├─→ [2] CUSTOMERS (Segmentation with pain intensity)
    ├─→ [3] COMPETITORS (Competitive landscape + gaps)
    ├─→ [4] ROOT CAUSES (Strategic analysis - most differentiated)
    └─→ [5] COSTS (MVP cost estimation)
```

---

## Section 1: OPPORTUNITY (Market Sizing)

### What It Does
Calculates **TAM → SAM → SOM** market funnel to estimate addressable market.

### Data Flow
```
3 Google searches:
  1. "{business_type} market size {metro}"
  2. "{business_type} industry report 2025-2026"
  3. "average revenue {business_type} {state}"
        ↓
Clean search results (top 10 snippets)
        ↓
LLM extracts TAM, SAM, SOM with methodology & confidence
        ↓
Validate: TAM > SAM > SOM (swap if confused)
```

### Output Format
```json
{
  "tam": {
    "value": 2800000000,
    "formatted": "$2.8B",
    "methodology": "Based on US population growth + market penetration rates",
    "confidence": "medium"
  },
  "sam": {
    "value": 340000000,
    "formatted": "$340M",
    "methodology": "Addressable by cold-chain delivery in metro areas",
    "confidence": "medium"
  },
  "som": {
    "value": 12000000,
    "formatted": "$12M",
    "methodology": "Year-1 capture: 1 city, premium segment",
    "confidence": "medium"
  },
  "funnel": {
    "tap_penetration": "12%",
    "reasoning": "Similar to food subscription startups (Blue Apron, HelloFresh)"
  }
}
```

### Current Intelligence
- ✅ Validates TAM > SAM > SOM (prevents inversions)
- ✅ Includes methodology explanation
- ✅ Confidence levels (low/medium/high)
- ✅ Location-aware (metro area considered)

### Current Issues
- ❌ No context from DISCOVER insights (LLM doesn't know pain intensity or market demand signals)
- ❌ Generic search queries (could be more targeted)
- ❌ No comparison to similar businesses
- ❌ Missing growth rate projections

---

## Section 2: CUSTOMERS (Segmentation)

### What It Does
Break target customers into **3-4 segments** with pain intensity, spending patterns, and acquisition channels.

### Data Flow
```
Use DISCOVER insights (evidence from Reddit, Yelp, etc.)
        ↓
LLM extracts 3-4 customer segments with:
  - Name (e.g., "Health-conscious professionals")
  - Description (lifestyle + needs)
  - Estimated size
  - Pain intensity (1-10)
  - Primary need
  - Spending pattern
  - Where to find them
        ↓
Normalize pain_intensity to 1-10
        ↓
Sort by pain_intensity (highest first)
```

### Output Format
```json
{
  "segments": [
    {
      "name": "Health-conscious professionals",
      "description": "Age 25-45, income $75k+, prioritize wellness",
      "estimated_size": 2300000,
      "pain_intensity": 8,
      "primary_need": "Quick access to organic, nutritious food",
      "spending_pattern": "Premium ($15-25/day on food)",
      "where_to_find": "Gym communities, Reddit r/fitness, wellness blogs"
    },
    {
      "name": "Fitness enthusiasts",
      "description": "Training for competitions, optimize nutrition",
      "estimated_size": 1100000,
      "pain_intensity": 7,
      "primary_need": "Consistent nutrition matching workout schedule",
      "spending_pattern": "Subscribe to services ($300-600/month)",
      "where_to_find": "Fitness forums, CrossFit communities, Instagram"
    }
  ]
}
```

### Current Intelligence
- ✅ Pain intensity normalized to 1-10 scale
- ✅ Segments sorted by pain (highest pain first)
- ✅ Includes spending patterns
- ✅ Includes acquisition channels ("where to find them")
- ✅ Uses DISCOVER evidence context

### Current Issues
- ❌ No connection to DISCOVER insights (could reference specific evidence)
- ❌ Size estimates generic (not validated against market data)
- ❌ No competitive positioning (how your solution is better)
- ❌ Missing willingness-to-pay signals from DISCOVER

---

## Section 3: COMPETITORS (Competitive Landscape)

### What It Does
Identify **4-8 direct and indirect competitors** with their strengths, weaknesses, and gaps.

### Data Flow
```
Build competitor queries from DECOMPOSE:
  - "{business_type} comparison"
  - "best alternatives to [competitor]"
  - "{business_type} vs traditional model"
        ↓
3-5 Serper queries, 8 results each = 24-40 competitor mentions
        ↓
Clean and format:
  - Competitor name
  - Location
  - Rating
  - Price range
  - Key strength
  - Key gap
  - Threat level (low/medium/high)
        ↓
Sort by threat_level (high first)
```

### Output Format
```json
{
  "competitors": [
    {
      "name": "Juice Generation (NYC-based)",
      "location": "New York, Los Angeles",
      "rating": 4.2,
      "price_range": "$12-18 per juice",
      "key_strength": "Premium brand, multiple locations, health-focused community",
      "key_gap": "Limited delivery, only East Coast, expensive pricing",
      "threat_level": "high",
      "url": "https://juicegeneration.com"
    },
    {
      "name": "BluePrint Cleanse (Inactive - acquired)",
      "location": "Historical (NYC-based)",
      "rating": 3.8,
      "price_range": "$65-125 per day cleanse",
      "key_strength": "Premium positioning, celebrity endorsements, all-organic",
      "key_gap": "Acquisition by Dish Network, unclear operations, no innovation",
      "threat_level": "low",
      "url": null
    }
  ],
  "unfilled_gaps": [
    "Affordable organic juice delivery (most players premium-only)",
    "Subscription flexibility (most require commitment)",
    "Regional expansion (mostly coastal cities)"
  ]
}
```

### Current Intelligence
- ✅ Threat level prioritization (high → medium → low)
- ✅ Identifies unfilled gaps in market
- ✅ Includes ratings and pricing
- ✅ Includes URLs for verification
- ✅ Mix of direct and indirect competitors

### Current Issues
- ❌ No connection to DISCOVER pain points (should reference specific unmet needs)
- ❌ No market share estimates
- ❌ No timeline of competitor actions (growth, acquisition, shutdown)
- ❌ Missing pricing elasticity analysis
- ❌ No "beat sheet" (how you're different)

---

## Section 4: ROOT CAUSES (Strategic Analysis) ⭐ Most Differentiated

### What It Does
Answer **"What are the 3-5 core problems your business solves?"** with strategic depth.

### Data Flow
```
CONTEXT AGGREGATION:
- From COMPETITORS: Their gaps
- From CUSTOMERS: Their primary needs
- From OPPORTUNITY: Market SOM estimate
- From DECOMPOSE: Business type + target market
        ↓
LLM uses ACCUMULATED CONTEXT to derive root causes
        ↓
For each root cause:
  1. Title (the core problem)
  2. Explanation (why this matters)
  3. Your move (how to address it as founder)
  4. Difficulty (easy/medium/hard to solve)
        ↓
Sort by difficulty (easy first - quick wins)
```

### Output Format
```json
{
  "root_causes": [
    {
      "cause_number": 1,
      "title": "Long wait times at juice bars (operational friction)",
      "explanation": "Customers spend 10-15 min waiting during rush hours. This reduces repeat purchases and limits customer lifetime value. Competitors haven't solved this with delivery models.",
      "your_move": "Build subscription model with home delivery + mobile ordering to eliminate wait times entirely",
      "difficulty": "easy"
    },
    {
      "cause_number": 2,
      "title": "Lack of cold-chain logistics (supply chain gap)",
      "explanation": "Most juice shops can't deliver without losing quality/freshness. Blue Apron & HelloFresh solved this for meals; no one has solved for cold-pressed juice.",
      "your_move": "Partner with local cold-storage providers OR invest in insulated packaging + next-day delivery logistics",
      "difficulty": "medium"
    },
    {
      "cause_number": 3,
      "title": "Premium positioning only (market segmentation gap)",
      "explanation": "Competitors charge $15-25 per juice. This locks out middle-income customers ($40k-75k/year) who value health but can't afford premium.",
      "your_move": "Offer tiered subscriptions: Basic ($8/day) made from seasonal fruit, Premium ($15/day) organic cold-pressed",
      "difficulty": "hard"
    }
  ]
}
```

### Current Intelligence
- ✅ **BEST IN CLASS:** Uses aggregated context from 3 previous sections
- ✅ Strategic reasoning (not just surface-level)
- ✅ Actionable "your_move" for each cause
- ✅ Difficulty assessment (helps prioritize execution)
- ✅ Explains WHY (not just WHAT)
- ✅ Sorted by difficulty (easy wins first)
- ✅ Higher temperature (0.5 vs 0.3) allows more creative reasoning

### Current Issues
- ❌ Could strengthen by citing specific DISCOVER evidence
- ❌ No prioritization framework (which root cause matters most?)
- ❌ Missing dependency analysis (cause A blocks cause B?)
- ❌ No resource requirements per cause

---

## Section 5: COSTS (MVP Cost Estimation)

### What It Does
Estimate **MVP cost range** ($min-$max) with breakdown by category.

### Data Flow
```
LLM estimates MVP costs for:
  - Engineering (dev, design, QA)
  - Operations (legal, accounting, insurance)
  - Marketing (launch, customer acquisition)
  - Infrastructure (servers, payment processing)
        ↓
Output min/max range
        ↓
Validate: min < max (swap if confused)
```

### Output Format
```json
{
  "total_range": {
    "min": 50000,
    "max": 100000,
    "formatted": "$50k - $100k"
  },
  "breakdown": [
    {
      "category": "Engineering",
      "range": {"min": 20000, "max": 40000},
      "items": "App development, backend, QA, design"
    },
    {
      "category": "Operations",
      "range": {"min": 5000, "max": 10000},
      "items": "Legal, accounting, insurance, permits"
    },
    {
      "category": "Marketing & Launch",
      "range": {"min": 15000, "max": 30000},
      "items": "Landing page, pre-launch community, paid ads"
    },
    {
      "category": "Infrastructure & Payment",
      "range": {"min": 5000, "max": 15000},
      "items": "Servers, payment processing, delivery partnerships"
    },
    {
      "category": "Working Capital",
      "range": {"min": 5000, "max": 5000},
      "items": "Initial inventory/supply chain setup"
    }
  ],
  "note": "Assumes founder is unpaid. Add $60k-100k/year for co-founder salary."
}
```

### Current Intelligence
- ✅ Category breakdowns (not just lump sum)
- ✅ Min/max ranges (realistic uncertainty)
- ✅ Includes working notes
- ✅ Validates min < max ordering

### Current Issues
- ❌ Not connected to business specifics (should reference location, business_type)
- ❌ No timeline (6 weeks? 6 months?)
- ❌ Missing funding runway (months of operation?)
- ❌ No comparison to similar businesses

---

## Current Optimization: Prior Context

The system **accumulates context** as user clicks through sections:

```python
# Frontend sends prior_context to each new section
await analyzeSection({
  section: "rootcause",
  insight: {...},
  decomposition: {...},
  prior_context: {
    "opportunity": {...},    // Results from Tab 1
    "customers": {...},      // Results from Tab 2
    "competitors": {...}     // Results from Tab 3
  }
})
```

**ROOT CAUSES benefits from this** - it references gaps, pain points, and market size from prior sections.

**OPPORTUNITY, CUSTOMERS, COMPETITORS could benefit more** - currently don't reference DISCOVER insights or each other.

---

## Key Metrics

| Section | API Calls | Time | Tokens | Context Used |
|---------|-----------|------|--------|--------------|
| **Opportunity** | 3 Google searches | 3-5s | 2000 | Decomp only |
| **Customers** | 0 (uses DISCOVER) | 2-3s | 2000 | Decomp + Insight |
| **Competitors** | 3-5 Google searches | 4-6s | 3000 | Decomp + Insight |
| **Root Causes** | 0 (cached) | 3-4s | 3000 | All prior sections ⭐ |
| **Costs** | 0 (cached) | 2-3s | 1000 | Decomp only |
| **TOTAL** | 6-8 Google searches | 15-20s | ~11k tokens | ~4-5s per user click |

---

## Summary: Current State

### Strengths
✅ Lazy-loaded (fast initial load, details on demand)
✅ ROOT CAUSES section is genuinely intelligent (uses all context)
✅ Data ingestion (real market data from Google)
✅ Validation logic (prevents TAM < SAM inversions)
✅ Sorted smartly (threat levels, pain intensity, difficulty)

### Gaps
❌ OPPORTUNITY & CUSTOMERS don't reference DISCOVER insights
❌ COMPETITORS misses pricing analysis and market share
❌ Missing competitive positioning ("beat sheet")
❌ No funding runway calculations
❌ Could batch LLM calls (currently 1 LLM per section click)

---

## Next Improvements (Optional)

1. **Batch LLM calls** - Send OPPORTUNITY + CUSTOMERS + COMPETITORS in 1 LLM call (30% faster)
2. **Add DISCOVER context** - Reference specific insights with evidence in each section
3. **Competitive positioning** - Add "Why you win" vs each competitor
4. **Funding runway** - Costs + monthly burn → runway months
5. **Market timing** - Is this the right time to enter? (trend analysis)
