# TAB 2: DISCOVER - Complete Working & Output

## What DISCOVER Does

DISCOVER takes the decomposed business structure and **scans Reddit + Google** to find real market signals:
- Pain points customers are expressing
- Market trends being discussed
- Willingness to pay (price signals)
- Market size indicators
- Customer preferences and frustrations

**Goal**: Find 3-5 high-confidence insights backed by real evidence from real people.

---

## How DISCOVER Works (7 Steps)

### **Step 1: Input from DECOMPOSE**
```json
{
  "business_type": "meal prep delivery service",
  "location": {
    "city": "Austin",
    "state": "TX",
    "county": "Travis",
    "metro": "Austin-Round Rock-San Marcos"
  },
  "target_customers": ["busy professionals", "health-conscious"],
  "price_tier": "mid-market",
  "search_queries": [
    "meal prep delivery Austin TX",
    "healthy meal subscriptions Austin",
    "meal prep for busy professionals"
  ],
  "subreddits": ["Austin", "Entrepreneur", "HealthyFood", "RemoteWork"]
}
```

---

### **Step 2: Scrape Reddit Posts**
Searches each subreddit using first search query + keywords

**Example Search**: "meal prep delivery Austin"

```
Subreddit: r/Austin
Posts Found: 23 relevant discussions
├─ User: "I wish there was a good meal prep service in Austin"
├─ User: "Spending $400/month on takeout, need alternative"
├─ User: "Would pay $15/meal if quality was consistent"
└─ ...18 more posts

Subreddit: r/RemoteWork
Posts Found: 31 relevant discussions
├─ User: "WFH = no time to meal prep, always buying takeout"
├─ User: "Looking for time-saving solutions"
└─ ...29 more posts
```

**Data Extracted from Each Post**:
- Post title
- Post content (first 200 chars)
- Author
- Upvote count
- Comment count
- Post date
- URL

**Budget**: 60 posts max (to avoid overload)

---

### **Step 3: Run Google Search Queries**
Searches Google for each search query

**Example Queries**:
1. "meal prep delivery Austin TX"
2. "healthy meal subscriptions Austin"
3. "meal prep for busy professionals"
4. "time-saving meal solutions"
5. "affordable meal delivery Austin"

**Data Retrieved Per Query**:
- 10 search results per query
- Snippet text
- URL
- Domain
- Publication date

**Typical Results**:
```
Query: "meal prep delivery Austin"
├─ Result 1: Freshly.com blog post "6 Meal Prep Trends 2024"
├─ Result 2: Google News article "Meal Delivery Market Growth"
├─ Result 3: Yelp reviews for local competitors
├─ Result 4: YouTube video "Time-Saving Meal Prep Tips"
└─ ...6 more results
```

---

### **Step 4: Clean Data**
Remove duplicates, low-quality content, spam

**Before Cleaning**:
- 60 Reddit posts
- 50 Google search results
- **Total**: 110 raw items

**After Cleaning**:
- Remove duplicates (same content mentioned twice)
- Remove spam/bot posts
- Remove low-relevance results
- Keep only substantive content
- **Total**: ~80 quality items

---

### **Step 5: Merge & Categorize**
Group similar items by theme

**Example Categories**:
1. **Pain Points**: Time constraints, meal prep difficulty, quality issues
2. **Willingness to Pay**: "$15/meal", "would pay premium for quality"
3. **Market Trends**: Growth of meal subscriptions, health consciousness
4. **Competitive Issues**: Complaints about existing services
5. **Market Size**: Number of professionals affected

---

### **Step 6: Sample for LLM Analysis**
Pick best examples from each category

**Budget**: 80 posts max for LLM processing
- 15-20 from Reddit
- 20-30 from Google search results
- Balanced across categories

**LLM Prompt** (summarized):
```
From these 80 posts and articles about meal prep services:
1. Extract pain points customers are expressing
2. Score each insight on:
   - Frequency (how often mentioned?)
   - Intensity (how strong is the emotion?)
   - Willingness to Pay (price signals)
   - Market Size (how many people affected?)
3. Generate 3-5 key market insights
4. Provide evidence from the posts
```

---

### **Step 7: Score & Rank Insights**
Calculate confidence score for each insight

**Scoring Formula**:
```
Composite Score = (
  frequency_score (0-100) × 0.25 +
  intensity_score (0-100) × 0.25 +
  willingness_to_pay_score (0-100) × 0.25 +
  market_size_score (0-100) × 0.25
)
```

Result: **0-100 score** (higher = more confident)

---

## Output Schema

### **Full DiscoverResponse**
```json
{
  "sources": [
    {
      "name": "Reddit r/Austin",
      "type": "reddit",
      "post_count": 23
    },
    {
      "name": "Reddit r/RemoteWork",
      "type": "reddit",
      "post_count": 31
    },
    {
      "name": "Google Search",
      "type": "google",
      "post_count": 50
    }
  ],

  "insights": [
    {
      "id": "insight_001",
      "type": "pain_point",
      "title": "Busy professionals struggle to maintain healthy eating habits due to time constraints",
      "score": 92.5,
      "frequency_score": 95,
      "intensity_score": 88,
      "willingness_to_pay_score": 90,
      "mention_count": 34,

      "evidence": [
        {
          "quote": "I spend 3+ hours per week on meal prep. Would definitely use a service if it was reliable.",
          "source": "reddit",
          "source_url": "https://reddit.com/r/Austin/comments/...",
          "score": 98,
          "upvotes": 145,
          "date": "2024-03-15"
        },
        {
          "quote": "WFH means I have no time for cooking. Currently spending $400/month on takeout.",
          "source": "reddit",
          "source_url": "https://reddit.com/r/RemoteWork/comments/...",
          "score": 95,
          "upvotes": 87,
          "date": "2024-03-10"
        },
        {
          "quote": "The #1 barrier to healthy eating is time management for professionals",
          "source": "google",
          "source_url": "https://blog.healthline.com/...",
          "score": 82,
          "upvotes": null,
          "date": "2024-02-20"
        }
      ],

      "source_platforms": ["reddit", "google"],
      "audience_estimate": "15K+ professionals in Austin metro",
      "confidence": "high",
      "confidence_reason": "34 mentions across 3+ platforms with consistent emotion and urgency"
    },

    {
      "id": "insight_002",
      "type": "willingness_to_pay",
      "title": "Professionals willing to pay $12-18/meal for quality, convenience, and nutritional transparency",
      "score": 88.0,
      "frequency_score": 92,
      "intensity_score": 85,
      "willingness_to_pay_score": 95,
      "mention_count": 28,

      "evidence": [
        {
          "quote": "Would happily pay $15/meal if the quality was consistent and nutritionally transparent",
          "source": "reddit",
          "source_url": "https://reddit.com/r/HealthyFood/comments/...",
          "score": 98,
          "upvotes": 112,
          "date": "2024-03-12"
        },
        {
          "quote": "$12-18 range feels fair for premium meal prep with fresh, local ingredients",
          "source": "reddit",
          "source_url": "https://reddit.com/r/Austin/comments/...",
          "score": 94,
          "upvotes": 78,
          "date": "2024-03-08"
        }
      ],

      "source_platforms": ["reddit", "google"],
      "audience_estimate": "$120M+ market opportunity at $15/meal",
      "confidence": "high",
      "confidence_reason": "12 explicit price mentions in $12-18 range with positive sentiment"
    },

    {
      "id": "insight_003",
      "type": "market_trend",
      "title": "Meal subscription services growing 25% YoY with increasing corporate adoption",
      "score": 84.5,
      "frequency_score": 88,
      "intensity_score": 82,
      "willingness_to_pay_score": 80,
      "mention_count": 21,

      "evidence": [
        {
          "quote": "The meal delivery market is growing 25% annually as remote work increases",
          "source": "google",
          "source_url": "https://techcrunch.com/meal-delivery-trends-2024",
          "score": 92,
          "upvotes": null,
          "date": "2024-02-15"
        }
      ],

      "source_platforms": ["google"],
      "audience_estimate": "$4.2B+ market",
      "confidence": "medium",
      "confidence_reason": "Trend documented in multiple industry reports, less direct user demand signal"
    }
  ]
}
```

---

## Understanding Each Output Field

### **Sources** (Where data came from)
```json
{
  "name": "Reddit r/Austin",
  "type": "reddit",
  "post_count": 23
}
```
- **name**: Display name of source
- **type**: Source type (reddit, google, yelp, twitter, etc)
- **post_count**: How many relevant items found in this source

### **Insights** (Key discoveries)
```json
{
  "id": "insight_001",
  "type": "pain_point",
  "title": "Busy professionals struggle to maintain healthy eating habits...",
  "score": 92.5,
  ...
}
```

**Insight Types**:
- **pain_point**: Problem customers are experiencing
- **unmet_want**: Something customers want but can't find
- **market_gap**: Opportunity competitors aren't filling
- **trend**: Market movement (growth, decline, shift)
- **willingness_to_pay**: Price signals from customers

**Score Components**:
- **frequency_score** (0-100): How often this is mentioned? (5 times = low, 50 times = high)
- **intensity_score** (0-100): How strongly do people feel? (casual mention = low, angry complaint = high)
- **willingness_to_pay_score** (0-100): Does this indicate price acceptance? (explicit "$15/meal" = high)
- **score** (0-100): Composite of all four signals
- **mention_count**: How many times this appeared across sources
- **confidence**: high | medium | low (based on cross-source validation)

### **Evidence** (Proof)
```json
{
  "quote": "I spend 3+ hours per week on meal prep...",
  "source": "reddit",
  "source_url": "https://reddit.com/r/Austin/comments/...",
  "score": 98,
  "upvotes": 145,
  "date": "2024-03-15"
}
```

- **quote**: Actual text from post/article
- **source**: Where it came from (reddit, google, yelp, etc)
- **source_url**: Clickable link to original post
- **score**: Confidence in this specific evidence (0-100)
- **upvotes**: Community validation (higher = more people agree)
- **date**: When this was posted (fresh = more current demand)

---

## Real Example: Complete DISCOVER Output

```
INPUT: Meal prep delivery service for busy professionals in Austin

DISCOVERED INSIGHTS:

┌─ INSIGHT 1: Pain Point (Score: 92.5) ✓ HIGH CONFIDENCE
│  "Busy professionals struggle to maintain healthy eating habits"
│
│  Evidence:
│  ├─ 34 mentions across 3+ platforms
│  ├─ "Spend $400/month on takeout, need alternative" (145 upvotes)
│  ├─ "3 hours/week on meal prep is unsustainable" (112 upvotes)
│  ├─ "WFH = no time to cook" (87 upvotes)
│  └─ Appears in r/Austin, r/RemoteWork, r/HealthyFood
│
│  Audience: 15K+ professionals in Austin metro
│  What it means: High pain point, urgent need, large audience
│
├─ INSIGHT 2: Willingness to Pay (Score: 88.0) ✓ HIGH CONFIDENCE
│  "$12-18 per meal is acceptable price point"
│
│  Evidence:
│  ├─ 28 explicit price mentions in $12-18 range
│  ├─ "Would pay $15/meal if quality was consistent" (112 upvotes)
│  ├─ "$12-18 feels fair for premium local ingredients" (78 upvotes)
│  └─ Multiple sources confirm this range
│
│  Market Opportunity: 200K+ professionals × $15/meal = $120M+
│  What it means: Price signal is strong, can sustain margin
│
├─ INSIGHT 3: Market Trend (Score: 84.5) ✓ MEDIUM CONFIDENCE
│  "Meal subscriptions growing 25% YoY"
│
│  Evidence:
│  ├─ TechCrunch: "Meal delivery market growing 25% annually"
│  ├─ McKinsey: "Remote work driving healthy food demand"
│  ├─ Multiple industry reports
│  └─ But less direct user demand signal than Insight 1
│
│  Market Size: $4.2B+ globally
│  What it means: Tailwind, but indirect signal
│
├─ INSIGHT 4: Competitive Gap (Score: 81.0) ✓ MEDIUM CONFIDENCE
│  "Existing services have quality/delivery/trust issues"
│
│  Evidence:
│  ├─ Freshly reviews: "Meals arrived warm 3/5 times" (2.8 stars)
│  ├─ Factor reviews: "Not enough meal variety" (3.5 stars)
│  └─ Common complaints: Logistics, menu repetition, cost
│
│  What it means: Opportunity to differentiate on quality/reliability
│
└─ INSIGHT 5: Demographics (Score: 79.0) ✓ MEDIUM CONFIDENCE
   "Primary audience: Remote workers, busy professionals 25-45"

   Evidence:
   ├─ r/RemoteWork discussions heavy (31 posts)
   ├─ r/FatFIRE mentions (high income) (18 posts)
   ├─ Multiple mentions of "work-from-home" lifestyle
   └─ Income level appears to be $80K+

   What it means: Affluent, remote, health-conscious segment

═══════════════════════════════════════════════════════════════
SUMMARY FOR FOUNDER
═══════════════════════════════════════════════════════════════

✓ Strong pain point: 15K+ professionals spending $300-500/month
✓ Clear price signal: Will pay $15/meal for quality
✓ Market growing: 25% YoY tailwind
✓ Gap to fill: Existing services have trust/quality issues
✓ Audience ready: Remote workers actively discussing need

OVERALL CONFIDENCE: HIGH (92/100)
- Multiple cross-platform validation
- High engagement on posts (100+ upvotes)
- Explicit willingness to pay
- Large addressable market
- Current competitors have weak points

NEXT STEP: ANALYZE (Deep dive on opportunity)
```

---

## How DISCOVER Connects to Other Tabs

### **→ ANALYZE Tab**
Uses: Best insights from DISCOVER
Does: Validates market size, competitive positioning, success factors

```
DISCOVER found: "Professionals willing to pay $12-18/meal"
ANALYZE verifies: Austin metro has 200K+ professionals → $120M market
```

### **→ VALIDATE Tab**
Uses: Target audience identified in DISCOVER
Does: Recruits people from those communities, tests willingness to pay

```
DISCOVER found: r/RemoteWork + r/Austin are prime communities
VALIDATE recruits: 50+ early testers from those subreddits
```

---

## Key Metrics Explained

| Metric | Range | What It Means |
|--------|-------|---------------|
| **score** | 0-100 | Overall insight confidence (80+ = strong signal) |
| **frequency_score** | 0-100 | How often mentioned (5 times = 40, 50 times = 90) |
| **intensity_score** | 0-100 | How strongly felt (casual = 30, urgent need = 90) |
| **willingness_to_pay_score** | 0-100 | How clear is price signal (no mention = 0, "$15/meal" = 95) |
| **mention_count** | 5-100+ | Total times across all sources |
| **confidence** | high/med/low | Based on cross-platform validation |
| **upvotes** | 0-500+ | Community validation (higher = more agree) |

---

## Decision Rules

**When to move forward to ANALYZE**:
- ✓ At least 1 insight with score 85+
- ✓ Multiple cross-platform validation
- ✓ Clear audience identified
- ✓ Willingness to pay signal present

**When to reconsider the idea**:
- ✗ No insights above 70
- ✗ Single-source validation only
- ✗ Price resistance evident
- ✗ Market trending downward

---

## Performance Notes

- **Speed**: 2-5 minutes (depends on Reddit API, Google Search API)
- **Posts analyzed**: 80-200 items
- **LLM calls**: 1 call to extract all insights
- **Cache**: Results cached for 30 days per business_type/city/state

