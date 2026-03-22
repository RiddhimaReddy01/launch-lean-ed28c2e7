# DISCOVER: LLM Prompt Reference & Expected Output

## Quick Summary of Changes

### What Changed
```
OLD:  Posts → Keyword analysis → Hardcoded scores → Response
      (Intensity=4, WTP=3, always)

NEW:  Posts → LLM Intelligence → Extracted signals → Composite score → Response
      (Intensity=1-10, WTP=1-10, Market Size=1-10, Urgency=1-10)
```

### Files Modified
1. **templates.py**: Added `discover_extract_signals_system()` + `discover_extract_signals_user()`
2. **discover.py**: Added `_extract_insights_with_signals()` LLM call
3. **discover.py**: Updated `_post_process()` to use LLM-extracted values
4. **ranking_service.py**: Updated composite score to prefer LLM values over heuristics

---

## LLM System Prompt (Exact)

### Prompt Name
`discover_extract_signals_system(business_type, city, state) → str`

### Full Text
```
You are a market research analyst analyzing customer conversations about [business_type] in [city], [state].

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
{
  "insights": [
    {
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
    }
  ]
}

RULES:
- Merge related insights (don't list "wait times" and "service speed" separately)
- Prioritize: Common + High pain + Willingness-to-pay
- Each insight must be supported by actual quotes/data
- Be specific: "Long checkout process" vs vague "bad experience"
- Flag trends: Growing mentions vs persistent background issues
- Confidence = based on evidence quality and consistency across sources
```

---

## LLM User Prompt (Exact)

### Prompt Name
`discover_extract_signals_user(posts, business_type, city, state) → str`

### Format
```
Market Research Data for [business_type] in [city], [state]:
Source Summary: [N] Reddit posts + [M] Google/review results

CUSTOMER CONVERSATIONS:
[1] [REDDIT] (engagement: 45) "Post title here"
    > Post excerpt/snippet
[2] [GOOGLE_SEARCH] (engagement: 3.2) "Result snippet"
    > Description
...
[N+M] [SOURCE] (engagement: X) "Title"
    > Snippet

Analyze these [N+M] data points and extract key market insights.
For each insight, evaluate Intensity, Willingness-to-Pay, Market Size, and Urgency based on the evidence.
Return 8-12 prioritized insights.
```

### Real Example
```
Market Research Data for cold-pressed juice subscription in San Francisco, CA:
Source Summary: 12 Reddit posts + 8 Google/review results

CUSTOMER CONVERSATIONS:
[1] [REDDIT] (engagement: 45) "Waiting 15 min for juice during lunch is killing me"
    > Every day at noon the juice bar has a line. I usually just grab fast food instead.
[2] [REDDIT] (engagement: 32) "Anyone know delivery service for cold-pressed juice?"
    > Would pay $15/day if I could get it at my office. Tired of bar prices.
[3] [GOOGLE_SEARCH] (engagement: 4.2) "Pressed Juicery - too expensive but amazing"
    > Love the quality but $8 per juice is steep for every day. Would need subscription.
[4] [REDDIT] (engagement: 28) "Cold pressed juice is becoming mainstream"
    > Seems like it's the new fitness trend. More juice bars opening every month.
...
[20] [GOOGLE_SEARCH] (engagement: 3.8) "organic juice SF comparison"
    > Multiple options available in Bay Area, all premium pricing

Analyze these 20 data points and extract key market insights.
For each insight, evaluate Intensity, Willingness-to-Pay, Market Size, and Urgency based on the evidence.
Return 8-12 prioritized insights.
```

---

## Expected LLM Output (Example)

### JSON Structure
```json
{
  "insights": [
    {
      "id": "ins_001",
      "type": "pain_point",
      "title": "Long wait times at juice bars",
      "explanation": "Customers report 10-20 minute wait times during peak hours (lunch, post-workout). This drives customers to competitive fast-food options instead. Multiple sources mention time as barrier to adoption.",
      "intensity": 7,
      "willingness_to_pay": 5,
      "market_size": 8,
      "urgency": 6,
      "evidence_summary": "Reddit posts from fitness communities report regular 15min+ waits. Google reviews mention 'quick service' as competitive advantage. Time-constrained professionals (fitness enthusiasts, busy workers) affected.",
      "customer_quote": "Waiting 15 min for juice during lunch is killing me. I usually just grab fast food instead.",
      "source_platforms": ["reddit", "google_search"],
      "mention_count": 8,
      "confidence": "high"
    },
    {
      "id": "ins_002",
      "type": "unmet_want",
      "title": "Demand for affordable juice delivery to office",
      "explanation": "Customers want convenience of office delivery but at sustainable pricing. Current delivery options (premium juice bars) charge $10-20 per drink. Gap: No affordable ($8-12/day) delivery subscription exists.",
      "intensity": 6,
      "willingness_to_pay": 7,
      "market_size": 7,
      "urgency": 7,
      "evidence_summary": "Multiple Reddit posts asking 'is there a delivery service?' with explicit price mentions ($15/day willingness). Competitors exist but premium-only. Growing fitness/wellness trend driving demand.",
      "customer_quote": "Would pay $15/day if I could get it at my office. Tired of bar prices.",
      "source_platforms": ["reddit", "google_search"],
      "mention_count": 6,
      "confidence": "high"
    },
    {
      "id": "ins_003",
      "type": "market_gap",
      "title": "Premium pricing locks out middle-income customers",
      "explanation": "Current market dominated by $8-12/drink premium players. Middle-income customers ($50-75k salary) want cold-pressed juice but price ($60-80/month) unsustainable. No budget alternative exists.",
      "intensity": 5,
      "willingness_to_pay": 4,
      "market_size": 9,
      "urgency": 6,
      "evidence_summary": "Google reviews consistently mention 'expensive for daily use'. Industry reports show juice bars target affluent customers only. Huge TAM in middle-market fitness segment.",
      "customer_quote": "Love the quality but $8 per juice is steep for every day. Would need subscription.",
      "source_platforms": ["google_search"],
      "mention_count": 5,
      "confidence": "medium"
    },
    {
      "id": "ins_004",
      "type": "trend",
      "title": "Cold-pressed juice becoming mainstream fitness trend",
      "explanation": "Shift from protein shakes to cold-pressed juice among fitness communities. Multiple Reddit posts reference 'trending', 'becoming mainstream'. New juice bars opening across SF. Market acceleration evident.",
      "intensity": 4,
      "willingness_to_pay": 6,
      "market_size": 7,
      "urgency": 8,
      "evidence_summary": "Reddit fitness communities showing rapid adoption. 'Seems like it's the new fitness trend' - multiple recent posts. More juice bars opening monthly. Instagram/social proof of popularity.",
      "customer_quote": "Cold pressed juice is becoming mainstream. More juice bars opening every month.",
      "source_platforms": ["reddit"],
      "mention_count": 4,
      "confidence": "high"
    }
  ]
}
```

---

## Signal Extraction Examples

### Example 1: Intensity = 7 (High)
```
Raw data:
  Reddit post: "My kid's allergy was so bad I was DESPERATE for help.
               Spent $500/month on tutors, finally found one that works."

LLM extraction:
  - Strong emotion: "desperate"
  - Financial sacrifice: "$500/month spent"
  - Health impact: "allergy" (kid's well-being)
  - Duration: Suggests ongoing critical need

Result: intensity = 8 (or 7 if less certain)
```

### Example 2: Willingness-to-Pay = 8 (Premium)
```
Raw data:
  Google review: "Subscription is $200/month. Worth it because my test scores
                 went from 65% to 85%. Best investment I made for my future."

LLM extraction:
  - Explicit high price: "$200/month"
  - ROI mentality: "best investment"
  - Multiple subscriptions: Willing to pay for multiple services
  - Emotional satisfaction: "worth it"

Result: willingness_to_pay = 8-9 (premium tier)
```

### Example 3: Market Size = 7 (Large)
```
Raw data:
  - Reddit: 45+ posts about AI tutoring (r/education, r/learnprogramming, r/parents)
  - Google: 300+ results for "AI tutoring reviews"
  - News: "$200B EdTech market, growing 15%/year"
  - Competitors: Chegg, Wyzant, Tutor.com, ClassDojo (all well-funded)

LLM extraction:
  - Volume: 45+ posts across multiple subreddits
  - Platform diversity: Multiple communities discussing
  - Industry data: Large market with institutional players
  - Competitor density: 4+ well-funded companies

Result: market_size = 8-9 (large market, 100K+ people)
```

### Example 4: Urgency = 6 (Growing)
```
Raw data:
  Reddit (Jan 2025): "AI tutoring is getting way better"
  Reddit (Feb 2025): "More startups in AI tutoring space now"
  Reddit (Mar 2025): "College admissions tougher than ever, AI tutors help"
  Google Trends: +40% growth in "AI tutoring" searches YoY
  News (Mar 2025): "3 new AI tutoring companies received Series A funding"

LLM extraction:
  - Recent trend mentions: "getting better", "more startups"
  - Acceleration signal: Month-to-month increase in mentions
  - Market catalyst: College admissions getting harder
  - VC activity: Series A funding recent

Result: urgency = 6-7 (growing trend, not yet explosive)
```

---

## Integration Points

### In discover.py
```python
# Line 73-80 (NEW)
llm_insights = await _extract_insights_with_signals(
    merged_sampled, business_type, city, state
)

# Function implementation
async def _extract_insights_with_signals(posts, business_type, city, state):
    system_prompt = discover_extract_signals_system(business_type, city, state)
    user_prompt = discover_extract_signals_user(posts, business_type, city, state)

    response = await call_llm(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.4,
        max_tokens=2000,
        json_mode=True,
    )

    return json.loads(response)
```

### In ranking_service.py
```python
# Lines 28-39 (UPDATED)
# Uses LLM-extracted market_size if available:
if "market_size" in insight and insight["market_size"] != 0:
    market_size = _clamp(insight.get("market_size", 5))
else:
    # Fallback to heuristic
    market_size = min(10.0, (evidence_count * 1.2) + (source_count * 1.5))

# Uses LLM-extracted urgency if available:
if "urgency" in insight and insight["urgency"] != 0:
    urgency = _clamp(insight.get("urgency", 5))
else:
    # Fallback to heuristic
    urgency = 8.0 if mention_count > 20 else 5.0
```

---

## Testing the New System

### Test Case 1: Cold-Pressed Juice Delivery
```
Input: business_type="Cold-pressed juice subscription"
       city="San Francisco"
       state="CA"

Expected Output:
- 8-12 insights with varied intensity/WTP/market_size/urgency
- "Wait times" insight: high intensity (7-8), medium WTP (4-5)
- "Delivery demand" insight: high WTP (7-8), medium intensity (5-6)
- "Trending juice market" insight: high urgency (7-8)
- "Pricing gap" insight: large market size (8-9)

Confidence scores: Mix of high/medium/low based on evidence volume
```

### Test Case 2: AI Tutoring Platform
```
Input: business_type="AI-powered online tutoring"
       city=""
       state=""

Expected Output:
- Multiple insights with high willingness-to-pay (6-8)
- Strong trend/urgency signals (7-9) due to EdTech boom
- Large market sizes (7-10)
- References to student desperation + parent willingness to pay

Confidence: Mostly high/medium due to large evidence volume
```

### Test Failure Scenarios
```
If LLM call fails:
  → Logs warning: "LLM extraction failed, using keyword analysis"
  → Falls back to _fallback_insights()
  → Returns keyword-based insights (old behavior)
  → Response still valid, just less intelligent

If posts is empty:
  → Returns {"insights": []}
  → Post-process handles gracefully
  → User sees "No insights found" in UI
```

---

## Performance Metrics

### Time Breakdown
```
Fetch Reddit:        1-2s  (API call)
Fetch Google:        2-3s  (API call)
Merge+Dedupe:        100ms (memory)
Stratified Sample:   50ms  (CPU)
──────────────────────────
LLM Extraction:      1-2s  (NEW - hot path)
──────────────────────────
Format Response:     100ms (CPU)
Cache Store:        500ms (DB write)

TOTAL (cache miss):  5-7s (vs 4-6s old)
TOTAL (cache hit):   50ms (database lookup)
```

### Token Usage
```
System prompt: ~800 tokens
User prompt:   ~500 tokens (80 posts × 6 tokens/post + headers)
Completion:    ~500-800 tokens (8-12 insights × 60-100 tokens each)
─────────────────────────────
Total per call: ~1800-2100 tokens

Cost: ~$0.03 per discovery request (at Haiku pricing)
Cache hit savings: Every 7 days, skip LLM = $0.03 saved × N queries
```

---

## Rollback Plan

If new LLM-based approach causes issues:

1. **Immediate**: Set environment variable to disable LLM
   ```python
   if os.getenv("DISCOVER_USE_LLM", "true") == "false":
       return _fallback_insights(posts)  # Use old keyword method
   ```

2. **Graceful**: Already built-in exception handling
   ```python
   except LLMError:
       return _fallback_insights(posts)  # Automatic fallback
   ```

3. **Full Revert**: Revert commit, use old discover.py

No data loss - cached insights remain available for 7 days.

