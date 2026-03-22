# Tab Fixes: Minimal, User-Focused Implementation

**User POV:** Do only what matters. No over-engineering.

---

## DISCOVER Tab (Score: 7.6 → 8.2)

### Current State
✅ LLM extracts 4 signals (Intensity, WTP, Market Size, Urgency)
✅ Real evidence from communities

### What's Missing (User POV)
❌ Founder doesn't know sample size
❌ Founder doesn't know if "trending" is meaningful

### Minimal Fix (1 line of code)

**Add confidence display to each insight:**

```json
{
  "insights": [
    {
      "id": "ins_001",
      "title": "Wait times at juice bars",
      "intensity": 7,
      "confidence": "high",  // ← NEW
      "confidence_reason": "12 mentions across reddit/google"  // ← NEW
    }
  ]
}
```

**Why:** Founder sees "high confidence based on 12 mentions" vs "medium confidence based on 3 mentions"

**Implementation:**
```python
# In discover.py _post_process()
insight.confidence = raw.get("confidence", "medium")  # Already in LLM output
insight.confidence_reason = f"{mention_count} mentions across {len(source_platforms)} platforms"
```

**Time to implement:** 15 mins
**User impact:** High (founder can weight insights appropriately)

---

## ROOT CAUSES Tab (Score: 8.6 → 9.0)

### Current State
✅ Synthesizes all prior sections
✅ "Your move" = concrete actions
✅ Difficulty assessment

### What's Missing (User POV)
❌ Founder doesn't know resource needs
❌ Founder doesn't know if THEY can execute

### Minimal Fix (Add 2 fields)

```json
{
  "root_causes": [
    {
      "cause_number": 1,
      "title": "Long wait times",
      "your_move": "Build subscription + home delivery",
      "difficulty": "easy",
      "estimated_effort_weeks": 6,  // ← NEW
      "required_skills": ["backend", "mobile", "logistics"]  // ← NEW
    }
  ]
}
```

**Why:** Founder knows "easy = 6 weeks + I can do backend but need logistics hire"

**Implementation:**
```python
# In analyze.py analyze_section()
raw["estimated_effort_weeks"] = {"easy": 4-6, "medium": 8-12, "hard": 16+}[difficulty]
raw["required_skills"] = extract_skills_from_your_move(raw["your_move"])
```

**Time to implement:** 30 mins
**User impact:** High (founder can assess if this is executable)

---

## CUSTOMERS Tab (Score: 7.8 → 8.2)

### Current State
✅ 3-4 segments with pain intensity
✅ Acquisition channels
✅ Spending patterns

### What's Missing (User POV)
❌ Doesn't link to market size (segments sum to what % of SAM?)
❌ Founder doesn't know which segment to target first

### Minimal Fix (Add validation link)

```json
{
  "segments": [
    {
      "name": "Health-conscious professionals",
      "estimated_size": 2300000,
      "market_coverage": "15%",  // ← NEW (of OPPORTUNITY SAM)
      "rank_by_pain": 1,  // ← NEW (which to target first?)
      "pain_intensity": 8
    }
  ],
  "validation": {
    "total_segment_size": 5200000,
    "opportunity_sam": 34000000,
    "market_coverage_percent": "15%"
  }
}
```

**Why:** Founder sees "these segments = 15% of addressable market, target the highest pain first"

**Implementation:**
```python
# In analyze.py after CUSTOMERS section
segment_sizes = sum(seg['estimated_size'] for seg in segments)
sam = opportunity['sam']['value']
segments = sorted(segments, key=lambda s: s['pain_intensity'], reverse=True)
for i, seg in enumerate(segments):
    seg['rank_by_pain'] = i + 1
    seg['market_coverage'] = f"{(seg['estimated_size']/sam)*100:.0f}%"
```

**Time to implement:** 20 mins
**User impact:** Medium (founder can validate and prioritize)

---

## COMPETITORS Tab (Score: 6.5 → 7.2)

### Current State
✅ Identifies 4-8 competitors
✅ Threat levels
✅ Gaps

### What's Missing (User POV)
❌ Doesn't say who's winning (market share?)
❌ Doesn't say how to differentiate (beat sheet)

### Minimal Fix (Add "beat sheet" vs top competitor)

```json
{
  "competitors": [...],
  "top_threat": {
    "name": "Juice Generation",
    "reason": "Highest threat level, multiple locations"
  },
  "how_to_win": {
    "vs_top_threat": [
      "We're cheaper: $12/juice vs their $15-18",
      "We deliver: They delivery-limited, we do home delivery",
      "We're flexible: Monthly commitment optional, they require plan"
    ]
  }
}
```

**Why:** Founder understands "this is what we need to do to beat them"

**Implementation:**
```python
# In analyze.py after COMPETITORS section
top_threat = max(competitors, key=lambda c: threat_score(c))
how_to_win = extract_differentiation(decomp, top_threat, root_causes)
```

**Time to implement:** 45 mins (needs heuristics for differentiation)
**User impact:** Medium-high (founder has positioning strategy)

---

## DECOMPOSE Tab (Score: 6.8 → 7.2)

### Current State
✅ Extracts business_type, location
✅ Customers, pricing
✅ Search queries

### What's Missing (User POV)
❌ Doesn't explicitly state business model (B2B/B2C/Local/Marketplace)
❌ Founder can't select this, LLM infers it

### Minimal Fix (Add explicit business_model field)

```json
{
  "business_type": "Cold-pressed juice subscription",
  "business_model": "B2C",  // ← NEW (inferred + validated)
  "location": {...},
  "target_customers": [...]
}
```

**Why:** Downstream sections can use this explicitly instead of guessing

**Implementation:**
```python
# In decompose.py stage 2
# Add to decompose_stage2_system prompt:
# "Infer business_model: 'B2B' | 'B2C' | 'LOCAL' | 'MARKETPLACE'"

# Add validation
valid_models = ['B2B', 'B2C', 'LOCAL', 'MARKETPLACE']
if decomp['business_model'] not in valid_models:
    decomp['business_model'] = infer_model(decomp['business_type'])
```

**Time to implement:** 20 mins
**User impact:** Low-medium (improves downstream accuracy)

---

## OPPORTUNITY Tab (Score: 5.8 → 6.5)

### Current State
✅ Calculates TAM/SAM/SOM
✅ Includes methodology

### What's Missing (User POV)
❌ No validation (SOM matches CUSTOMERS market size?)
❌ Founder doesn't trust the numbers

### Minimal Fix (Add validation check)

```json
{
  "tam": {...},
  "sam": {...},
  "som": {...},
  "validation": {
    "customers_total_size": 5200000,
    "som_implies_customer_base": 8000,  // SOM/ACV
    "alignment": "GOOD" // or "WARNING" or "MISMATCH"
  }
}
```

**Why:** Founder sees "SOM of $12M means ~8k customers at $1.5k ACV - that matches our CUSTOMERS segments"

**Implementation:**
```python
# In analyze.py OPPORTUNITY section
from CUSTOMERS segment
total_addressable = sum(seg['estimated_size'] for seg in customers)
som_customers = som_value / avg_customer_value
if abs(som_customers - total_addressable) < 20%:
    alignment = "GOOD"
else:
    alignment = "MISMATCH"
```

**Time to implement:** 30 mins
**User impact:** Medium (founder gains confidence in numbers)

---

## COSTS Tab (Score: 4.8 → 6.0)

### Current State
✅ Breaks down by category
❌ Generic ranges
❌ No runway calculation

### What's Missing (User POV)
❌ Founder doesn't know "how long until we run out of money?"
❌ No burn rate visible

### Minimal Fix (Add 2 calculated fields)

```json
{
  "total_range": {"min": 50000, "max": 100000},
  "breakdown": [...],
  "monthly_burn": {"min": 5000, "max": 10000},  // ← NEW
  "runway_months": {"min": 5, "max": 20}  // ← NEW
}
```

**Why:** Founder instantly sees "spend $75k on MVP, burn $7.5k/month = 10 months runway"

**Implementation:**
```python
# In analyze.py COSTS section
monthly_burn = {
    "min": (total_min / 12) + 2000,  # 12 month amortize + ops
    "max": (total_max / 12) + 4000
}
runway_months = {
    "min": total_max / monthly_burn['max'],
    "max": total_min / monthly_burn['min']
}
```

**Time to implement:** 20 mins
**User impact:** Very high (founder knows survival timeline)

---

## Summary: Minimal Fixes

| Tab | Current | New Score | Fix Type | Time | Impact |
|-----|---------|-----------|----------|------|--------|
| **DISCOVER** | 7.6 | 8.2 | Add confidence reason | 15m | HIGH |
| **ROOT CAUSES** | 8.6 | 9.0 | Add effort + skills | 30m | HIGH |
| **CUSTOMERS** | 7.8 | 8.2 | Link to OPPORTUNITY SAM | 20m | MEDIUM |
| **COMPETITORS** | 6.5 | 7.2 | Add beat sheet | 45m | MEDIUM |
| **DECOMPOSE** | 6.8 | 7.2 | Explicit business_model | 20m | LOW |
| **OPPORTUNITY** | 5.8 | 6.5 | Validate with CUSTOMERS | 30m | MEDIUM |
| **COSTS** | 4.8 | 6.0 | Add runway calculation | 20m | VERY HIGH |

**Total implementation time:** ~3.5 hours

**Total user value:** Each founder immediately understands execution feasibility + survival runway + market validation

---

## Do These First (Priority Order)

### 1️⃣ COSTS Runway (20 mins) - USER CRITICAL
```
Founder needs to know: "How long can I survive?"
Without this: All other insights are useless (no $ to build)
```

### 2️⃣ ROOT CAUSES Effort (30 mins) - EXECUTION CLARITY
```
Founder needs to know: "Can I actually do this?"
Without this: Pretty insights, unclear if feasible
```

### 3️⃣ DISCOVER Confidence (15 mins) - SIGNAL QUALITY
```
Founder needs to know: "Is this based on 3 mentions or 300?"
Without this: Can't weight insights appropriately
```

### 4️⃣ COMPETITORS Beat Sheet (45 mins) - POSITIONING
```
Founder needs to know: "How am I different from the best competitor?"
Without this: No differentiation strategy
```

### 5️⃣ CUSTOMERS Market Coverage (20 mins) - VALIDATION
```
Founder needs to know: "Do my segments add up to a real market?"
Without this: Segments feel disconnected from OPPORTUNITY
```

### 6️⃣ OPPORTUNITY Validation (30 mins) - MARKET SENSE CHECK
```
Founder needs to know: "Are these numbers realistic?"
Without this: TAM/SAM/SOM feel made-up
```

### 7️⃣ DECOMPOSE Business Model (20 mins) - INFRASTRUCTURE
```
Founder needs to know: "Is this B2B or B2C?" (for downstream accuracy)
Without this: CUSTOMERS/COSTS guessing
```

---

## What NOT to Do

❌ Don't add detailed cost breakdowns (too granular)
❌ Don't add hiring timelines (not user need right now)
❌ Don't add competitor market share (hard to get accurate)
❌ Don't add sensitivity analysis (overcomplicate)
❌ Don't replace COSTS with GTM strategy yet (for demo, keep simple)

---

## Deployment Approach

1. **Immediately:** COSTS runway (1 line of code)
2. **This week:** ROOT CAUSES effort + DISCOVER confidence
3. **Next week:** COMPETITORS beat sheet
4. **Later:** CUSTOMERS linkage + OPPORTUNITY validation

All backward compatible. No breaking changes. Just adding fields to responses.

