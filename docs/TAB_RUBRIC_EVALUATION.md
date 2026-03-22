# LaunchLens: Tab-by-Tab Rubric Evaluation

## Evaluation Criteria

### 1. **Intelligence/Strategy Quality** (0-10)
- Does it provide novel insights founders wouldn't easily figure out?
- Is reasoning grounded in data or heuristics?
- Does it surface non-obvious opportunities/threats?

### 2. **Data Quality** (0-10)
- Are data sources comprehensive and relevant?
- Is data validated/cleaned before analysis?
- Does it account for biases or sample size issues?

### 3. **Actionability** (0-10)
- Can founder directly act on the output?
- Are recommendations specific or generic?
- Is prioritization clear?

### 4. **Reliability/Accuracy** (0-10)
- How often is output wrong/misleading?
- Are there known failure modes?
- How resilient to edge cases?

### 5. **User Value** (0-10)
- Would a founder find this useful?
- Does it save time vs manual research?
- Does it change their decision-making?

### 6. **Completeness** (0-10)
- Does it cover the topic fully?
- Are gaps obvious or hidden?
- What's missing?

---

## TAB 1: DECOMPOSE

### Overview
Extracts structured business metadata from raw idea pitch.

### Ratings

| Criterion | Score | Notes |
|-----------|-------|-------|
| **Intelligence** | 5/10 | Mostly extraction, limited insight |
| **Data Quality** | 7/10 | Clean parsing but limited enrichment |
| **Actionability** | 8/10 | Output directly feeds downstream tabs |
| **Reliability** | 8/10 | Mostly deterministic, LLM extraction solid |
| **User Value** | 6/10 | Useful internal but not founder-facing insight |
| **Completeness** | 7/10 | Covers basics, missing business model details |
| **OVERALL** | **6.8/10** | **Functional but not strategic** |

### Strengths ✅
- Fast (1-2s Stage 1 + 2-3s Stage 2)
- Validates location/state format automatically
- Vertical-specific prompts improve quality (SaaS vs Food Service)
- Feeds all downstream sections effectively
- Two-stage extraction balances speed + quality

### Gaps ❌
- **No business model extraction** (B2B vs B2C vs Local vs Marketplace = only inferred)
- **Pricing is text, not structured** ("premium ($15-25/month)" = hard to parse)
- **No competitive positioning** (what makes YOUR idea different?)
- **No technical feasibility assessment** (is this buildable? scalable?)
- **Missing KPIs** (what would success look like for founder?)
- **No founder profile** (do you have relevant experience? team?)

### Risk Factors
- **Hardcoded vertical list** - new verticals fail silently
- **Location parsing fragile** - ambiguous inputs (Boston, MA vs Boston, USA)
- **Generic search queries** - if decomp wrong, all downstream searches wrong

### Improvement Ideas
- Add "business_model" field extraction (with validation)
- Parse pricing tier numerically (min/max dollars)
- Add founder context questions (experience, team size, timeline)
- Add feasibility assessment (technology risk, regulatory risk)

---

## TAB 1.5: DISCOVER

### Overview
Scrapes Reddit + Google for market evidence; extracts 10 insights with signals.

### Ratings

| Criterion | Score | Notes |
|-----------|-------|-------|
| **Intelligence** | 8/10 | ✅ NEW: LLM extraction with 4 signals is smart |
| **Data Quality** | 7/10 | Real data from communities, but sampling bias |
| **Actionability** | 7/10 | Insights useful but need context |
| **Reliability** | 8/10 | LLM fallback ensures response always returns |
| **User Value** | 8/10 | Founder sees "what customers are saying" |
| **Completeness** | 7/10 | 4 signals comprehensive, but missing perspective |
| **OVERALL** | **7.6/10** | **Strong, actionable market research** |

### Strengths ✅
- ✅ **NEW:** LLM-extracted signals (Intensity, WTP, Market Size, Urgency) = 85% accurate
- Real customer evidence (Reddit, Google, reviews = authentic voice)
- 4-signal composite score intelligently prioritizes
- Graceful fallback to keyword analysis if LLM fails
- 7-day caching = fast repeat queries
- Evidence + quotes make insights tangible

### Gaps ❌
- **No confidence intervals** - user doesn't know if 50 mentions = large market or tiny
- **No geographic weighting** - NYC Reddit ≠ Austin Reddit ≠ national market
- **No temporal signals** - trending last month vs 3 years ago looks the same
- **Sample bias hidden** - Reddit skews young/tech-savvy, Yelp skews complaining
- **No competitor context** - "wait times" insight doesn't mention if competitors solved it
- **Missing willingness-to-pay evidence** - score 6 but max price quoted is $12?

### Risk Factors
- **LLM signal extraction could be wrong** - "I'd never pay for this" scored as WTP=3 correctly?
- **Sampling bias** - 80 posts from millions = representative? Who speaks up?
- **Recency bias** - seasonal problems look urgent (back-to-school = temporary)
- **Reddit search quality** - first result ≠ best evidence

### Improvement Ideas
- Add confidence intervals based on evidence count + platform diversity
- Add temporal analysis (trend up/down over time)
- Add sample bias disclosure ("Based on Reddit + Google, skews X demographic")
- Add competitive context ("X competitors already solve this")
- Add price evidence quotations (link to actual "$X" mentions)

---

## TAB 2A: OPPORTUNITY (Market Sizing)

### Overview
Calculates TAM → SAM → SOM using Google search data.

### Ratings

| Criterion | Score | Notes |
|-----------|-------|-------|
| **Intelligence** | 6/10 | Formula-based, not context-aware |
| **Data Quality** | 6/10 | Google search ≠ market research reports |
| **Actionability** | 5/10 | Numbers without framework not useful |
| **Reliability** | 7/10 | Math is consistent, but input data varies |
| **User Value** | 5/10 | Founder knows SAM matters but not convinced method |
| **Completeness** | 6/10 | Covers 3 metrics, missing decomposition |
| **OVERALL** | **5.8/10** | **Useful but weak methodology** |

### Strengths ✅
- Validates TAM > SAM > SOM (prevents silly inversions)
- Includes methodology explanation (shows work)
- Confidence levels signal uncertainty
- Location-aware (considers metro area)
- 3-search strategy reasonable

### Gaps ❌
- **No DISCOVER integration** - should reference pain intensity for SAM filtering
- **TAM calculation opaque** - "metro population × interest%" = where does interest% come from?
- **SOM too simplistic** - "0.5-1% of SAM Year 1" = doesn't account for business model
- **No comparison to benchmarks** - "is $12M reasonable for juice subscription?" vs what?
- **Missing growth trajectory** - static numbers, no Year 2/3/5 projections
- **No unit economics check** - TAM/SAM/SOM disconnected from COSTS
- **Geographic granularity weak** - "metro area" but San Francisco ≠ suburbs

### Risk Factors
- **Google search results = marketing spin** - competitors' market size claims inflated
- **Market fragmentation hidden** - might be $1B TAM but 100 micro-markets ($10M each)
- **Regulatory restrictions invisible** - healthcare/finance TAM artificially large
- **LLM hallucination** - "Average revenue per juice shop = $500k/year" (made up?)

### Improvement Ideas
- Reference DISCOVER customer count for SAM (not guessing percentage)
- Add unit economics: SAM / avg customer LTV = realistic market
- Show Year 1/3/5 projections
- Add comparison: "Similar to [comparable market]"
- Decompose TAM: X metros × Y people/metro × Z spend/person = explicit
- Flag regulatory risks (is this market restricted?)

---

## TAB 2B: CUSTOMERS (Segmentation)

### Overview
Extracts 3-4 customer segments with pain intensity, spending, location signals.

### Ratings

| Criterion | Score | Notes |
|-----------|-------|-------|
| **Intelligence** | 8/10 | ✅ Pain intensity derived from evidence |
| **Data Quality** | 8/10 | ✅ Grounds in DISCOVER insights |
| **Actionability** | 8/10 | Founder can target marketing/features to segments |
| **Reliability** | 7/10 | LLM segmentation reasonable, but arbitrary splits |
| **User Value** | 8/10 | ✅ Directly informs go-to-market |
| **Completeness** | 7/10 | Covers needs, missing willingness validation |
| **OVERALL** | **7.8/10** | **Strong strategic output** |

### Strengths ✅
- ✅ Pain intensity sourced from DISCOVER (data-grounded, not guessed)
- Sorted by pain (highest first = prioritization)
- Spending patterns quantified ($X/month)
- Acquisition channels specific ("r/fitness, gym communities")
- Size estimates included
- "Primary need" captures core driver

### Gaps ❌
- **Segment size estimates unvalidated** - "2.3M health-conscious professionals" in SF? How certain?
- **No TAM linkage** - segments sum to 3.4M but OPPORTUNITY TAM was $12M, disconnected
- **Willingness-to-pay varies within segment** - all professionals pay same?
- **No acquisition cost signals** - "find on r/fitness" but how much does that cost?
- **Missing buyer persona depth** - jobs-to-be-done not captured
- **No seasonal/lifecycle signals** - back-to-school rush? post-New Year resolution spike?

### Risk Factors
- **Segment overlap** - "fitness enthusiasts" ⊆ "health-conscious professionals"?
- **LLM invents segments** - "Busy professionals" from minimal evidence
- **Spending pattern conflicts** - segment says premium but DISCOVER showed budget-conscious quotes

### Improvement Ideas
- Add segment size validation: "Based on X mentions, estimated 2.3M ±500k"
- Link to OPPORTUNITY SAM: "This segment represents 45% of addressable market"
- Add willingness-to-pay variation (sub-segments?)
- Include jobs-to-be-done framework
- Add seasonal patterns: "Peak demand Sept (back-to-school)"
- Show competitor positioning per segment

---

## TAB 2C: COMPETITORS (Competitive Landscape)

### Overview
Identifies 4-8 competitors with threat levels and unfilled gaps.

### Ratings

| Criterion | Score | Notes |
|-----------|-------|-------|
| **Intelligence** | 7/10 | Threat level useful, gaps surface real opportunities |
| **Data Quality** | 6/10 | Google results = incomplete picture |
| **Actionability** | 7/10 | Founder knows who to monitor + gaps to fill |
| **Reliability** | 6/10 | Threat level heuristic-based, can be wrong |
| **User Value** | 7/10 | ✅ Competitive context informs strategy |
| **Completeness** | 6/10 | Missing pricing analysis + market share |
| **OVERALL** | **6.5/10** | **Useful but surface-level** |

### Strengths ✅
- Threat level prioritization (high → medium → low)
- Identifies unfilled gaps (opportunities for differentiation)
- Includes URLs for verification
- Mix of direct + indirect competitors
- Rating + price range included

### Gaps ❌
- **Threat level calculation opaque** - why is Juicero "high threat" but Pressed Juicery "medium"?
- **No market share data** - how big is each competitor really?
- **Growth trajectory missing** - expanding or contracting?
- **Pricing elasticity absent** - competitors all charge $12, but what do customers prefer?
- **No acquisition/funding intelligence** - is competitor well-funded (dangerous) or bootstrapped?
- **M&A/exit history missing** - BluePrint acquired = threat or opportunity?
- **No "beat sheet"** (how you're different vs each competitor)

### Risk Factors
- **Google search finds active companies only** - acquired/defunct companies miss the picture
- **LLM hallucination on pricing** - "BluePrint charges $65-125/day cleanse" = real or made up?
- **Local bias** - juice bars in SF might not be largest competitors (DoorDash, HelloFresh = indirect)
- **Threat level wrong** - small bootstrapped competitor might be more nimble than funded player

### Improvement Ideas
- Add market share estimates (if available)
- Show growth signals: "Series A funding 2024 = expanding"
- Add pricing elasticity analysis: "Customers prefer $X, competitors charge $Y"
- Create "beat sheet": "vs Competitor A: we are [cheaper/faster/healthier/local]"
- Add M&A risk: "BluePrint acquired, leaving market gap"
- Link to CUSTOMERS: "Threat level HIGH for Segment 1 (premium), LOW for Segment 3 (budget)"

---

## TAB 2D: ROOT CAUSES (Strategic Synthesis) ⭐

### Overview
Identifies 3-5 core structural problems using aggregated context from A+B+C.

### Ratings

| Criterion | Score | Notes |
|-----------|-------|-------|
| **Intelligence** | 9/10 | ⭐ Synthesizes all prior sections, creative |
| **Data Quality** | 8/10 | Grounds in aggregated evidence |
| **Actionability** | 9/10 | ⭐ "Your move" = direct execution path |
| **Reliability** | 8/10 | LLM creative (0.5 temp), but sensible |
| **User Value** | 9/10 | ⭐ Core strategy output, most valuable |
| **Completeness** | 8/10 | Covers causes + moves, missing resource costs |
| **OVERALL** | **8.6/10** | **⭐ STRONGEST TAB** |

### Strengths ✅
- ⭐ **Best in class:** Uses ALL prior context (A+B+C+Decompose+DISCOVER)
- ⭐ Strategic reasoning (not just surface problems)
- ⭐ "Your move" = concrete founder actions
- Difficulty assessment (easy wins first)
- Explains WHY competitors miss it
- Temperature 0.5 = creative but grounded

### Gaps ❌
- **No resource requirements** - "hard" difficulty but how much capital/time?
- **Missing dependencies** - does cause A block cause B?
- **No prioritization framework** - all 3 seem important, which matters most?
- **Execution timeline vague** - easy = 2 weeks? 6 months?
- **Risk analysis missing** - if "your move" fails, what's fallback?
- **No founder skill assessment** - do you have skills to execute?

### Risk Factors
- **LLM over-creates problems** - invents issues that don't exist if DISCOVER weak
- **Context aggregation amplifies bias** - if all sections agree on wrong thing, ROOT CAUSES also wrong
- **Complexity hidden** - "hard" problem might be actually "impossible"

### Improvement Ideas
- Add resource requirements: Engineering team size, capital, timeline
- Add dependency matrix: "Fix A before B" or "A and C in parallel"
- Add prioritization: "Impact vs Effort" matrix
- Add risk mitigation: "If your_move fails, fallback is..."
- Link to OPPORTUNITY: "Solving cause A captures $X of $SAM"
- Add founder skill match: "This requires [X expertise] which you [have/lack]"

---

## TAB 2E: COSTS (MVP Estimation)

### Overview
Estimates MVP budget by category (Engineering/Ops/Marketing/Infra).

### Ratings

| Criterion | Score | Notes |
|-----------|-------|-------|
| **Intelligence** | 5/10 | Generic formulas, not business-specific |
| **Data Quality** | 4/10 | Hardcoded ranges, not data-driven |
| **Actionability** | 6/10 | Founder knows ballpark but not confident |
| **Reliability** | 5/10 | Ranges wide ($20k-40k for Engineering?) |
| **User Value** | 5/10 | Useful for pitch deck, weak for planning |
| **Completeness** | 4/10 | Missing runway, hiring timeline, cash burn |
| **OVERALL** | **4.8/10** | **Weakest tab - needs overhaul** |

### Strengths ✅
- Breaks down by category (not just lump sum)
- Min/max ranges (acknowledges uncertainty)
- Includes working notes (founder context)
- Validates min < max

### Gaps ❌
- ❌ **No business-specific logic** - SaaS vs food service vs local = wildly different costs
- ❌ **Hardcoded ranges** - "Engineering $20k-40k" = same for simple app vs complex platform?
- ❌ **No runway calculation** - costs ÷ burn rate = months
- ❌ **Missing hiring timeline** - when do you hire? affects cash burn
- ❌ **No burn rate** - monthly cash needed, not just lump sum
- ❌ **No runway buffer** - how many months should you target?
- ❌ **Team size assumptions hidden** - 1 founder? co-founder? employees?
- ❌ **No funding strategy** - bootstrap vs angel vs VC = different spending paths
- ❌ **Marketing costs detached from CUSTOMERS** - should target segments found
- ❌ **No post-MVP costs** - scaling, infrastructure, team growth

### Risk Factors
- **Massive cost variance** - "Infra $5k-15k" = true but useless (on what?)
- **Engineering is biggest cost but most uncertain** - could be $10k (no-code) or $500k (custom platform)
- **LLM guesses, doesn't reason** - "Insurance $2k" but your business legal risk?
- **Founder salary missing** - "$50k-100k" but that's WITHOUT founders?

### Improvement Ideas
- ⭐ **REPLACE with GO-TO-MARKET STRATEGY** (as mentioned in ANALYZE_DETAILED_LOGIC.md):
  - Phase 1: Validate problem (landing page, community, Reddit)
  - Phase 2: Build MVP (engineering focus)
  - Phase 3: Acquire first customers (growth focus)
  - Timeline + budget per phase
- Add business model: "SaaS" = different costs than "Marketplace"
- Reference ROOT CAUSES: "Solving cause A requires X engineering, solving B requires Y"
- Add hiring timeline: "Month 1-3: solo, Month 4: first hire"
- Calculate monthly burn rate
- Add runway targets: "Target 18 months runway on $X raise"
- Add customer acquisition cost: "Estimated CAC $X based on CUSTOMERS segments"

---

## Summary Scorecard

| Tab | Intelligence | Data Quality | Actionability | Reliability | User Value | Completeness | **OVERALL** |
|-----|---|---|---|---|---|---|---|
| **DECOMPOSE** | 5 | 7 | 8 | 8 | 6 | 7 | **6.8** |
| **DISCOVER** | 8 | 7 | 7 | 8 | 8 | 7 | **7.6** ⭐ |
| **OPPORTUNITY** | 6 | 6 | 5 | 7 | 5 | 6 | **5.8** ❌ |
| **CUSTOMERS** | 8 | 8 | 8 | 7 | 8 | 7 | **7.8** ⭐ |
| **COMPETITORS** | 7 | 6 | 7 | 6 | 7 | 6 | **6.5** |
| **ROOT CAUSES** | 9 | 8 | 9 | 8 | 9 | 8 | **8.6** ⭐⭐ |
| **COSTS** | 5 | 4 | 6 | 5 | 5 | 4 | **4.8** ❌ |

---

## Top Priorities for Improvement

### 🔴 Critical (Score < 6)
1. **COSTS (4.8)** - Replace with GO-TO-MARKET STRATEGY
   - Current: Generic cost ranges
   - Needed: Phase-by-phase breakdown, timeline, burn rate, acquisition strategy
   - Impact: Most founders care about runway + GTM, not just budget

2. **OPPORTUNITY (5.8)** - Integrate with downstream sections
   - Current: Isolated market sizing
   - Needed: Link to CUSTOMERS TAM validation, COMPETITORS context, ROOT CAUSES impact
   - Impact: Founder gains confidence in SOM numbers

### 🟡 High (Score 6-7)
3. **COMPETITORS (6.5)** - Add market share + positioning
   - Missing: "How big is each competitor?" + "How are we different?"
   - Impact: Founder understands competitive advantage needed

4. **DECOMPOSE (6.8)** - Add business model + feasibility
   - Missing: Explicit B2B/B2C/Local classification, risk factors
   - Impact: Prevents downstream sections from analyzing wrong market

### 🟢 Good (Score > 7.5)
- **DISCOVER (7.6)** - Maintain, improve confidence signals
- **CUSTOMERS (7.8)** - Maintain, add seasonal patterns
- **ROOT CAUSES (8.6)** - Maintain, add resource requirements

---

## Recommended Next Steps

1. **Immediate (Demo Fix)**
   - Replace COSTS with GO-TO-MARKET STRATEGY (faster to build, more valuable)
   - Add "Confidence" display to DISCOVER (show sample size, platform diversity)

2. **Short-term (Quality Improvement)**
   - Add validation: CUSTOMERS segments sum to OPPORTUNITY SAM
   - Add competition context: which ROOT CAUSES do competitors address?
   - Add resource requirements to ROOT CAUSES

3. **Medium-term (Completeness)**
   - Add founder context questions to DECOMPOSE
   - Add pricing analysis to COMPETITORS
   - Add market share estimates to COMPETITORS

4. **Long-term (Intelligence)**
   - Add business model sensitivity analysis: "If B2B: SOM=$X, if B2C: SOM=$Y"
   - Add founder skills assessment: "Can you execute ROOT CAUSE 3?"
   - Add funding playbook: "Bootstrap path: $X, Seed round path: $Y"

