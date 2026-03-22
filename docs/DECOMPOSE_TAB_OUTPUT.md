# TAB 1: DECOMPOSE - Complete Output Breakdown

## What It Does
DECOMPOSE takes a raw business idea and breaks it down into structured components that feed into the entire research pipeline. It extracts:
- What type of business this is
- Where it operates (geography)
- Who the customers are
- Pricing positioning
- Where to research (domains, communities, review sites)
- What keywords to search for

---

## Input
```
Idea: "A sustainable, affordable meal prep delivery service for busy professionals in Austin"
```

---

## Output Schema

### 1. **business_type** (String)
The core business model classification
```
"meal prep delivery service"
```
- What you are: service type, industry, business model
- Used by: DISCOVER (find similar businesses), ANALYZE (market research), SETUP (operational planning)

---

### 2. **location** (Object)
Geographic breakdown of the market
```json
{
  "city": "Austin",
  "state": "TX",
  "county": "Travis",
  "metro": "Austin-Round Rock-San Marcos"
}
```
- **city**: Primary launch location
- **state**: State/region
- **county**: County for localized research
- **metro**: Metropolitan area (used for market size estimates)

**Purpose**: Narrows research to relevant geography. Different cities have different demand patterns.

---

### 3. **target_customers** (List of Strings)
Who you're trying to reach
```
[
  "busy professionals",
  "health-conscious individuals",
  "remote workers",
  "people with dietary restrictions",
  "corporate wellness program participants"
]
```

**How it's used**:
- DISCOVER: Search for pain points specific to each segment
- ANALYZE: Validate if each segment has enough demand
- SETUP: Design operations around customer needs
- VALIDATE: Tailor messaging and channels per segment

---

### 4. **price_tier** (String)
Where your pricing sits relative to competitors
```
"mid-market"
```

Options:
- **"economy"** - Budget-conscious, high volume, thin margins
- **"mid-market"** - Balance of quality and price
- **"premium"** - Quality-first, willing to pay more
- **"luxury"** - Exclusive, niche, high margins

**Used by**: SETUP (determines cost structure), VALIDATE (pricing in experiments)

---

### 5. **source_domains** (List of URLs)
Websites to research for competitive/market intelligence
```
[
  "freshly.com",
  "gobble.com",
  "sunbasket.com",
  "trifecta.com",
  "factor.com",
  "grubhub.com",
  "doordash.com",
  "austinfood.com",
  "austineats.com",
  "austintexas.gov"
]
```

**Purpose**:
- Identify existing competitors
- Understand pricing strategies
- Learn customer acquisition channels
- Check regulatory requirements

---

### 6. **subreddits** (List of Subreddit Names)
Communities where your target customers hang out
```
[
  "Austin",
  "Entrepreneur",
  "smallbusiness",
  "HealthyFood",
  "RemoteWork",
  "FatFIRE",
  "TimeManagement",
  "BusiestProfessionals",
  "DFWgeneralinfo"
]
```

**Why Reddit?**
- Real people discussing pain points
- Authentic demand signals (not marketing)
- Can search by keyword ("meal prep Austin", "meal delivery")
- High signal for niche markets

**Used by**: DISCOVER (extract pain points and willingness to pay)

---

### 7. **review_platforms** (List of Platform Names)
Where customers leave feedback about similar services
```
[
  "yelp",
  "google",
  "trustpilot",
  "capterra",
  "appstore",
  "playstore"
]
```

**What to find**:
- Customer satisfaction levels
- Top complaints (logistics, quality, packaging)
- Feature requests
- Pricing feedback

---

### 8. **search_queries** (List of Keywords/Phrases)
Google search queries to validate demand
```
[
  "meal prep delivery Austin TX",
  "healthy meal subscriptions Austin",
  "meal prep services Austin",
  "time-saving meal solutions",
  "affordable meal prep delivery",
  "corporate meal plans Austin",
  "vegan meal delivery Austin",
  "meal prep for busy professionals",
  "meal delivery Austin reviews",
  "meal subscription services comparison"
]
```

**How it works**:
- High search volume = high demand
- Related searches = common variations
- "Near me" searches = local intent
- Competitor comparisons = buyer research

**Used by**: DISCOVER (validate market demand through search trends)

---

## Complete Example Output (JSON)

```json
{
  "business_type": "meal prep delivery service",
  "location": {
    "city": "Austin",
    "state": "TX",
    "county": "Travis",
    "metro": "Austin-Round Rock-San Marcos"
  },
  "target_customers": [
    "busy professionals",
    "health-conscious individuals",
    "remote workers",
    "people with dietary restrictions",
    "corporate wellness participants"
  ],
  "price_tier": "mid-market",
  "source_domains": [
    "freshly.com",
    "gobble.com",
    "sunbasket.com",
    "trifecta.com",
    "factor.com"
  ],
  "subreddits": [
    "Austin",
    "Entrepreneur",
    "smallbusiness",
    "HealthyFood",
    "RemoteWork"
  ],
  "review_platforms": [
    "yelp",
    "google",
    "trustpilot",
    "capterra"
  ],
  "search_queries": [
    "meal prep delivery Austin TX",
    "healthy meal subscriptions",
    "meal prep for busy professionals",
    "affordable meal delivery Austin",
    "corporate meal plans Austin"
  ]
}
```

---

## How Each Field Flows to Next Tabs

### → DISCOVER Tab
Uses:
- `search_queries` - What to search for
- `subreddits` - Where to find discussions
- `target_customers` - Whose pain points to extract
- `location` - Geographic context

**Produces**: 3-5 insights about market demand

---

### → ANALYZE Tab
Uses:
- `business_type` - What market to analyze
- `location` - Market size for that geography
- `target_customers` - Customer segments to validate
- `price_tier` - Positioning in competitive landscape

**Produces**: Deep dive on opportunity (TAM, competitive analysis, success factors)

---

### → SETUP Tab
Uses:
- `business_type` - What operations to plan for
- `location` - Regional cost factors
- `price_tier` - Budget tier to design for
- `target_customers` - Team structure needed

**Produces**: Cost breakdown, suppliers, team plan, timeline

---

### → VALIDATE Tab
Uses:
- `target_customers` - Who to recruit for experiments
- `location` - Where to source validation participants
- `search_queries` - Ad copy for customer acquisition
- `subreddits` - Communities to post validation surveys

**Produces**: Validation metrics with CAC/LTV analysis

---

## Real Example: How Decomposition Drives Research

**Input Idea**: "A sustainable, affordable meal prep delivery service for busy professionals in Austin"

**Decomposition**:
- Business Type: `meal prep delivery service`
- Location: `Austin, TX`
- Target: `busy professionals, health-conscious`
- Price: `mid-market`

**DISCOVER Uses This To**:
- Search Reddit in r/Austin and r/RemoteWork for discussions about meal prep struggles
- Find evidence of willingness to pay (people saying "$15/meal is fair")
- Quantify audience size ("15K+ professionals in Austin metro")

**Example Discovery Result**:
- ✓ 34 Reddit posts about meal prep struggles
- ✓ "$12-18 per meal" mentioned 12 times as acceptable price
- ✓ "Time is my bottleneck" pain point appears 23 times
- **Insight Score**: 92/100 - High confidence demand signal

**ANALYZE Uses This To**:
- Market Size: Austin metro has 200K+ professionals → $120M addressable market
- Competitive: Found 8 direct competitors (Freshly, Factor, Gobble)
- Pricing: Mid-market positioning validates $14-16/meal price point

**SETUP Uses This To**:
- Cost Tier: MID tier ($75-100k) fits bootstrapped founders
- Suppliers: GrubHub API for delivery, local kitchen rental
- Team: Founder + part-time chef (not full team yet)

**VALIDATE Uses This To**:
- Target Audience: Recruit from r/Austin, LinkedIn remote workers
- Messaging: "Save 5 hours/week" resonates with busy professionals
- Channels: Email (b2b corporate wellness) + social media ads

---

## Key Insight

**Decomposition is the foundation.**

Every downstream analysis, every research direction, every operational decision traces back to how well you decomposed the initial idea.

- Bad decomposition → Research misses the real market
- Good decomposition → Research finds unmet demand efficiently

**The system validates that decomposition is correct by seeing if DISCOVER, ANALYZE, SETUP, and VALIDATE all align.**

If they don't align, you re-decompose.
