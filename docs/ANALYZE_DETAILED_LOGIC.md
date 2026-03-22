# ANALYZE Tab: Detailed Calculation Logic

## Section A: OPPORTUNITY Sizing (TAM → SAM → SOM)

### What Gets Passed to LLM

```python
SYSTEM PROMPT:
"Calculate market sizing for a {business_type} in {city}, {state} ({metro} metro).

Using the market data provided and your knowledge of the area, calculate:
- TAM: Total addressable market for this business type in {metro}
- SAM: Serviceable available market matching the specific pain point
- SOM: Serviceable obtainable market - realistic year-1 capture for a single location"

USER PROMPT:
"Business: Cold-pressed juice subscription
Location: San Francisco, CA
Target customers: Health-conscious professionals, Fitness enthusiasts

Selected insight: Long wait times at juice bars during rush hours
Evidence:
  - "Always have to wait 10+ min for fresh juice" (from reddit)
  - "Would switch to subscription if same-day delivery" (from yelp)

Additional context:
- Cold pressed juice market size CA 2026
- Average revenue juice bar CA
- Juice bar industry report 2025"
```

### How LLM Calculates

**TAM (Total Addressable Market):**
```
1. Extract metro area population (SF Bay = 7.7M people)
2. Estimate % interested in juice/health (25-30% = 2M people)
3. Apply spending pattern ($1-2 per day on beverages = $400-800/year)
4. TAM = 2M people × $600/year = $1.2B

LLM uses: Population × interest rate × annual spending
Result: "$2.8B" (broader estimate including all beverage alternatives)
```

**SAM (Serviceable Available Market):**
```
1. Filter TAM to metro area only (SF Bay Area = 7.7M)
2. Filter to target customers: health-conscious professionals + fitness (25% = 1.9M)
3. Filter to willing to try subscription (60% = 1.1M)
4. SAM = 1.1M × $600/year = $660M

LLM applies: Metro population × {specific segment %} × {annual spend}
Result: "$340M" (addressable by your specific solution)
```

**SOM (Serviceable Obtainable Market):**
```
1. Year 1 reality: single location (SF only, not all Bay Area)
2. Realistic market capture: 10-20% of willing segment
3. Conservative estimate: 0.5% of SAM
4. SOM = $660M × 0.5% = $3.3M per location × 4 locations = $12M

Or:
1. SF population: 875k
2. Target segment: 25% = 219k
3. Early adopters (willing to try subscription): 60% = 131k
4. Year 1 realistic capture: 5-10% = 6.5-13k customers
5. Revenue per customer: $1500-2000/year
6. SOM = 10k customers × $1500 = $15M

LLM uses: Single location + conservative capture rate
Result: "$12M" (realistic for scrappy founder, year 1)
```

### Post-Processing

```python
# Validate TAM > SAM > SOM
tam_val = extract_number("tam")        # 2800000000
sam_val = extract_number("sam")        # 340000000
som_val = extract_number("som")        # 12000000

if tam_val < sam_val:
    swap(tam_val, sam_val)  # LLM confused, fix it
```

### Output
```json
{
  "tam": {
    "value": 2800000000,
    "formatted": "$2.8B",
    "methodology": "US juice market + healthy beverage category. 7.7M Bay Area × 25% interested × $600 annual spend",
    "confidence": "medium"
  },
  "sam": {
    "value": 340000000,
    "formatted": "$340M",
    "methodology": "Health-conscious segment in Bay Area only. 1.9M × $600 annual spend - 50% penetration",
    "confidence": "medium"
  },
  "som": {
    "value": 12000000,
    "formatted": "$12M",
    "methodology": "Year 1: SF location only. 0.5% SAM capture = 10k customers × $1.2k annual value",
    "confidence": "medium"
  }
}
```

---

## Section B: CUSTOMERS Segmentation & Pain Intensity

### What Gets Passed to LLM

```python
SYSTEM PROMPT:
"Generate 3-4 customer segments for a {business_type} in {city}.

For each segment, return:
{
  "segments": [{
    "name": "Segment name",
    "description": "2-3 sentences",
    "estimated_size": number,
    "pain_intensity": 1-10,
    "primary_need": "What they care about most",
    "spending_pattern": "How much they spend on alternatives",
    "where_to_find": "Online + offline hangouts"
  }]
}

Sort by pain_intensity descending."

USER PROMPT:
"Business: Cold-pressed juice subscription
Location: San Francisco, CA
Target customers: Health-conscious professionals, Fitness enthusiasts

Selected insight: Long wait times at juice bars during rush hours
Evidence:
  - "Always have to wait 10+ min for fresh juice" (from reddit)
  - "Would switch to subscription if same-day delivery" (from yelp)
  - [5 more evidence quotes]"
```

### How LLM Determines Pain Intensity

**Evidence-Based Scoring:**
```
Evidence 1: "Always have to wait 10+ min"
  → Wait = friction = HIGH pain (8/10)

Evidence 2: "Would switch to subscription if same-day delivery"
  → Word "switch" = strong dissatisfaction (9/10)

Evidence 3: "Most competitors don't have delivery"
  → No alternatives = trapped (7/10)

Pain Intensity = Average of evidence signals
  → (8 + 9 + 7) / 3 = 8/10 (ROUNDED)
```

**Persona-Specific Pain Intensity:**

```
For "Health-conscious professionals":
- Evidence: "frustration with fast food alternatives"
- Evidence: "willing to pay premium for health"
- Pain signal: Want health but current options suck
- Pain intensity: 8/10 (strong unmet need)

For "Fitness enthusiasts":
- Evidence: "need consistent nutrition for training"
- Evidence: "current options don't match workout schedules"
- Pain signal: Time-synchronized need
- Pain intensity: 7/10 (structured but manageable)
```

### Post-Processing

```python
# Normalize pain_intensity to 1-10
for segment in segments:
    pi = segment["pain_intensity"]
    if pi > 10:
        pi = pi / 10  # Fix 80 → 8
    segment["pain_intensity"] = min(10, max(1, round(pi)))

# Sort by pain (highest first)
segments.sort(key=lambda s: s["pain_intensity"], reverse=True)
```

### Output
```json
{
  "segments": [
    {
      "name": "Health-conscious professionals",
      "description": "Age 25-45, income $75k+, prioritize wellness. Work long hours (8am-6pm+), value time-saving solutions",
      "estimated_size": 2300000,
      "pain_intensity": 8,  ← HIGH (wait times frustrate them)
      "primary_need": "Quick access to organic, nutritious food without leaving work",
      "spending_pattern": "Premium ($15-25/day on food, willing to pay for convenience)",
      "where_to_find": "Gym communities (24 Hour Fitness, Apple Park), Reddit r/fitness, wellness blogs, LinkedIn"
    },
    {
      "name": "Fitness enthusiasts",
      "description": "Training for competitions, optimize nutrition for performance. Need predictability and timing",
      "estimated_size": 1100000,
      "pain_intensity": 7,  ← MEDIUM-HIGH (structure matters)
      "primary_need": "Consistent nutrition matching workout schedule (pre/post workout timing)",
      "spending_pattern": "Subscribe to services ($300-600/month), less price-sensitive than professionals",
      "where_to_find": "Fitness forums (r/fitness, r/bodyweightfitness), CrossFit communities, Strava, Instagram #fitfam"
    }
  ]
}
```

---

## Section C: COMPETITORS Analysis

### What Gets Passed to LLM

```python
SYSTEM PROMPT:
"Analyze competitors for a {business_type} in {city}, {state}.

Using the search results and review data provided:
{
  "competitors": [{
    "name": "Business name",
    "location": "Specific location",
    "rating": star rating,
    "price_range": "$ or specific range",
    "key_strength": "What they do well",
    "key_gap": "What they miss (use evidence from reviews)",
    "threat_level": "low | medium | high",
    "url": "Yelp or Google link"
  }],
  "unfilled_gaps": ["Gap that NO competitor fills"]
}

Include 4-8 competitors. Sort by threat_level (high first)."

USER PROMPT:
"Business: Cold-pressed juice subscription
Location: San Francisco, CA

Additional context:
[Top 20 competitor search results with snippets, ratings, links]"
```

### How LLM Determines Threat Level

**Analysis Framework:**

```
Competitor 1: "Juice Generation (NYC-based)"
  - Market presence: Established, multiple locations
  - Rating: 4.2/5 (strong)
  - Price: $12-18/juice (premium, matches target)
  - Gap from reviews: "Limited delivery, only East Coast"
  - Your advantage: You're in CA, they're not (yet)
  → Threat level: HIGH (if they expand west, serious competition)

Competitor 2: "BluePrint Cleanse (Acquired)"
  - Market presence: Acquired by Dish Network (zombie)
  - Rating: 3.8/5 (declining)
  - Price: $65-125/day (ultra-premium)
  - Gap: "Acquisition, unclear operations, innovation stopped"
  - Your advantage: You're nimble, they're not
  → Threat level: LOW (no longer innovating)

Competitor 3: "Local juice bars (generic)"
  - Market presence: Fragmented, many small players
  - Rating: 3.5-4.0 (decent)
  - Price: $8-12/juice (competitive)
  - Gap from reviews: "Long waits, inconsistent, no delivery"
  - Your advantage: Direct solution to their problem
  → Threat level: MEDIUM (many players, no clear leader)
```

**Threat Scoring:**
```
High =
  - Established brand + good reviews
  - Growing (new locations, new products)
  - Solving similar problem
  - In your geography OR expanding

Medium =
  - Established but not innovating
  - Not in your geography
  - Different price point
  - Missing key features

Low =
  - Declining reviews
  - Acquired/pivoting
  - Not solving your problem
  - Outdated operations
```

### Post-Processing

```python
# Validate threat_level
valid_threats = {"low", "medium", "high"}
for competitor in competitors:
    if competitor["threat_level"] not in valid_threats:
        competitor["threat_level"] = "medium"

# Sort by threat (high first)
threat_order = {"high": 0, "medium": 1, "low": 2}
competitors.sort(key=lambda c: threat_order[c["threat_level"]])
```

### Output
```json
{
  "competitors": [
    {
      "name": "Juice Generation",
      "location": "New York, Los Angeles",
      "rating": 4.2,
      "price_range": "$12-18 per juice",
      "key_strength": "Premium brand, multiple locations, health community",
      "key_gap": "Limited delivery, only East Coast, expensive",
      "threat_level": "high",
      "url": "https://juicegeneration.com"
    }
  ],
  "unfilled_gaps": [
    "Affordable organic juice delivery (most players premium-only)",
    "Subscription flexibility (most require commitment)",
    "Regional expansion (mostly coastal cities)"
  ]
}
```

---

## Section D: ROOT CAUSES (Strategic Synthesis)

### What Gets Passed to LLM

```python
SYSTEM PROMPT:
"You are a startup strategist. Identify 3-5 ROOT CAUSES for why this gap exists.

These should be STRUCTURAL, ECONOMIC, or REGULATORY reasons — NOT just 'nobody thought of it.'

Return JSON:
{
  "root_causes": [{
    "cause_number": 1,
    "title": "Concise title",
    "explanation": "2-3 sentences with SPECIFIC evidence",
    "your_move": "SPECIFIC, ACTIONABLE counter-strategy",
    "difficulty": "easy | medium | hard"
  }]
}

This is the MOST DIFFERENTIATED section. Go deep. Reference local specifics."

USER PROMPT:
"Business: Cold-pressed juice subscription in SF
Location: San Francisco, CA
Target customers: Health-conscious professionals, Fitness enthusiasts

Selected insight: Long wait times at juice bars
Evidence: [5 quotes from Reddit, Yelp]

Additional context:
COMPETITORS:
- Juice Generation: Gap = Limited delivery, only East Coast
- BluePrint: Gap = Acquired, unclear operations
- Local bars: Gap = Long waits, inconsistent

CUSTOMERS:
- Health pros: Pain = 8 (wait times frustrate)
- Fitness: Pain = 7 (structure matters)

MARKET:
SOM estimate: $12M (year 1, SF location only)"
```

### How LLM Synthesizes Root Causes

**Root Cause Logic:**

```
OBSERVATION: Competitors don't have delivery, just physical locations
QUESTION: Why not?

ROOT CAUSE 1: "Cold-chain logistics are expensive"
  Evidence: BluePrint had premium pricing ($125/day), hard to scale
  Your move: Partner with local cold-storage (not build yourself)
  Difficulty: medium (partnerships exist, just need to negotiate)

ROOT CAUSE 2: "Unit economics work for $12+ per drink only"
  Evidence: Most competitors $12-18+ pricing
  Question: Can you make $8 drinks work?
  Your move: Seasonal fruit sourcing (cheaper in CA), lower margin acceptable early
  Difficulty: hard (requires perfect ops to make thin margins work)

ROOT CAUSE 3: "Market shift just started (subscription economy)"
  Evidence: No juice player has solved subscription yet
  Question: Is this timing? Or structural barrier?
  Your move: First-mover advantage - move fast before big players copy
  Difficulty: easy (you just need to execute faster)
```

**References Prior Sections:**
```
- Competitor gaps: "No one offers same-day delivery"
- Customer pain: "Pain intensity 8/10 on wait times"
- Market opportunity: "$12M SOM suggests this is real demand"

Synthesis: These 3 signals together mean:
  1. Gap exists (competitors can't/won't solve)
  2. Customer pain is real (not theoretical)
  3. Market is big enough to matter ($12M)
  → Root causes are worth addressing
```

### Post-Processing

```python
# Validate difficulty
valid_diff = {"easy", "medium", "hard"}
for cause in causes:
    if cause["difficulty"] not in valid_diff:
        cause["difficulty"] = "medium"

# Sort by difficulty (easy wins first)
diff_order = {"easy": 0, "medium": 1, "hard": 2}
causes.sort(key=lambda c: diff_order[c["difficulty"]])
```

### Output
```json
{
  "root_causes": [
    {
      "cause_number": 1,
      "title": "Long wait times (operational friction)",
      "explanation": "Customers spend 10-15 min waiting during rush (9am-1pm). This reduces repeat visits and limits LTV. Existing juice bars can't scale beyond walk-in capacity.",
      "your_move": "Build subscription + home delivery to eliminate waits. Partner with local delivery (not build from scratch). Target pre-orders (predict demand) vs real-time.",
      "difficulty": "easy"
    },
    {
      "cause_number": 2,
      "title": "Cold-chain logistics barrier",
      "explanation": "Most juice needs immediate consumption or expensive cold-storage. BluePrint failed partly due to logistics costs. This locks competitors to premium pricing ($15+/drink).",
      "your_move": "Test with insulated + ice packs first (low cost). Then upgrade to partnered cold-chain if volume justifies. SOM $12M suggests this pays off.",
      "difficulty": "medium"
    },
    {
      "cause_number": 3,
      "title": "Subscription economy shift (timing)",
      "explanation": "No juice startup has cracked subscription delivery yet. Blue Apron solved it for meals, Grubhub for prepared food. First-mover advantage still open.",
      "your_move": "Move fast. Acquire first 1000 subscribers in SF in 6 months (proof point). Then expand to LA (where Juice Generation has brand but no delivery). Capture before they evolve.",
      "difficulty": "easy"
    }
  ]
}
```

---

## Section E: What to Replace COSTS With?

Since SETUP tab already handles MVP costing, here are better options:

### Option 1: FINANCIAL PROJECTIONS (Year 1-3 P&L)
```
Input: OPPORTUNITY SOM, CUSTOMERS spending patterns, COSTS from SETUP
Output: Revenue projection, CAC, LTV, break-even month

Example:
Year 1:
- Revenue: 10k subscribers × $1500/year = $15M (vs SOM $12M)
- COGS: 40% = $6M
- Operating: $8M (delivery, customer service, tech)
- Result: -$3M (expected, reinvesting in growth)

Break-even: Month 18 at current unit economics
Profitability: Year 3 at 20% COGS improvements
```

### Option 2: GO-TO-MARKET STRATEGY
```
Input: CUSTOMERS segments, COMPETITORS, ROOT CAUSES
Output: Phased acquisition strategy

Phase 1 (Months 1-2): Beta in Reddit r/fitness (low-cost, high engagement)
Phase 2 (Months 2-4): Launch in Nextdoor SF (local, word-of-mouth)
Phase 3 (Months 4-6): Paid ads targeting gym communities (Instagram, Facebook)

CAC target: <$50/customer
LTV target: >$1500 (30x multiple)
Acquisition channel mix: 40% organic, 30% community, 30% paid
```

### Option 3: UNIT ECONOMICS & SENSITIVITY
```
Input: COSTS, target customers, market conditions
Output: Sensitivity analysis

Base case: $8/day subscription (profit margin 30%)
  - Retention: 80% monthly
  - LTV: $1440/customer (12 months)
  - CAC: $50/customer
  - LTV/CAC: 28.8x (great)

Sensitivity:
- If retention drops to 70%: LTV → $1260 (still 25x)
- If COGS rise 10%: margin → 27% (acceptable)
- If CAC rises to $75: LTV/CAC → 19x (still good)

Break-even CAC: $48 (at 80% retention, current COGS)
```

### Option 4: RISK ANALYSIS & MITIGATION
```
Input: All prior sections
Output: Key risks + mitigation strategies

Risk 1: Logistics costs higher than projected
  - Mitigation: Pre-negotiated partnerships with 3 delivery providers
  - Trigger: If delivery costs > 25% revenue
  - Action: Pivot to local pickup hubs in high-density neighborhoods

Risk 2: Competitor response (Juice Generation launches CA + delivery)
  - Mitigation: Establish brand loyalty before they move
  - Trigger: If JG announces SF delivery
  - Action: Aggressive referral program, lock in 12-month subscriptions

Risk 3: Market size smaller than SOM estimate
  - Mitigation: Start with fitness segment only (confirmed pain = 8/10)
  - Trigger: If CAC > 2x assumption after Month 4
  - Action: Pivot messaging to B2B (gyms, CrossFit boxes)
```

---

## Recommendation: GO-TO-MARKET STRATEGY (Option 2)

**Why:**
- ROOT CAUSES tells you the problems
- SETUP tells you the costs
- GTM strategy tells you HOW to acquire customers
- Bridges gap between "we built it" → "who buys it"
- Directly actionable for founder
- Can reference all prior sections naturally

**Structure:**
```
Phase 1: Find early adopters (Reddit, Nextdoor)
Phase 2: Build community (loyal customers, word-of-mouth)
Phase 3: Scale with paid ads (use data from phase 1-2)

For each phase:
- Channels to use
- Target segment
- Message/positioning
- Success metrics
- Timeline
- Budget (reference SETUP tab)
```

This replaces generic "COSTS" with strategic "MARKET CAPTURE" intelligence.
