# ANALYZE Tab - Functionality, Logic, User Interaction

## Quick Summary
The ANALYZE tab is a **5-section lazy-loaded module** where users click each section to analyze different aspects of their market. No section is mandatory - users control which analyses matter to them.

---

## FUNCTIONALITY: What the Tab Does

### 5 Independent Analysis Sections

```
User clicks section → Section loads on-demand → LLM analyzes → Results display
```

| Section | Input | Processing | Output |
|---------|-------|-----------|--------|
| **OPPORTUNITY** | Business type + location | Search for market data (3 queries), LLM sizing | TAM, SAM, SOM + funnel |
| **CUSTOMERS** | Insight evidence from DISCOVER | LLM segmentation (no search) | 3-4 customer segments |
| **COMPETITORS** | Business type + location | Search for competitors (5-8 queries), LLM analysis | 4-8 competitors + gaps |
| **ROOT CAUSE** | All prior sections | LLM strategic analysis (no search) | 3-5 structural reasons for gap |
| **COSTS** | Business type + location | LLM estimation (no search) | Cost breakdown: real estate, equipment, permits, operations |

### Key Logic
1. **User clicks section tab** → Section state changes to "loading"
2. **Backend starts processing** → May fetch search data + call LLM
3. **Results return** → Component renders with structured data
4. **User can click other sections** → They load independently (no waiting for all 5)

---

## LOGIC: How Each Section Works

### OPPORTUNITY (Market Sizing)

**Logic Flow:**
```
Input: "meal prep delivery" in Austin, TX
  ↓
Search 3 queries:
  - "meal prep delivery market size Austin metro"
  - "meal prep delivery industry report 2025 2026"
  - "average revenue meal prep delivery Texas"
  ↓
Get 15 search results (5 per query)
  ↓
Clean & extract titles + snippets
  ↓
Send to LLM with prompt:
  "Based on this market data, calculate TAM/SAM/SOM for meal prep in Austin"
  ↓
LLM returns:
  - TAM: $150M (total Austin metro opportunity)
  - SAM: $45M (serviceable to busy professionals)
  - SOM: $2.5M (realistic Year 1 for 1 location)
  ↓
Display with confidence levels
```

**Data Quality:**
- TAM ≥ SAM ≥ SOM (enforced - swap if wrong)
- Numbers extracted from LLM response (e.g., "$150M" → 150000000)
- Confidence: low/medium/high based on evidence

---

### CUSTOMERS (Segmentation)

**Logic Flow:**
```
Input: Business type + target customers + DISCOVER insight evidence
  ↓
No search - uses existing data
  ↓
Send to LLM:
  "Based on the customer evidence, create 3-4 distinct segments"
  ↓
LLM returns:
  [
    {
      "name": "Busy Professionals",
      "pain_intensity": 9,
      "estimated_size": 25000,
      "primary_need": "Time-saving with healthy food",
      "spending_pattern": "$300-500/month on dining"
    },
    {
      "name": "Fitness Enthusiasts",
      "pain_intensity": 7,
      ...
    }
  ]
  ↓
Post-process:
  - Normalize pain_intensity to 1-10 range
  - Sort by pain_intensity (highest first)
  - Cap at 4 segments max
  ↓
Display: Cards ranked by pain level
```

**Key Logic:**
- Highest pain segment = biggest opportunity
- Can target different segments with different pricing
- "Where to find them" helps marketing strategy

---

### COMPETITORS (Landscape)

**Logic Flow:**
```
Input: Business type + location
  ↓
Search 5-8 competitor queries:
  - "meal prep delivery Austin"
  - "healthy meal plans Austin reviews"
  - "meal prep alternatives Austin"
  - etc.
  ↓
Get 40-80 competitor results
  ↓
Extract: name, location, rating, reviews, price range
  ↓
Send to LLM:
  "Analyze these competitors - what's their strength, gap, and threat level?"
  ↓
LLM returns:
  [
    {
      "name": "Factor Meals",
      "threat_level": "high",
      "key_strength": "Large menu, macro targeting",
      "key_gap": "Premium pricing, no local story"
    },
    {
      "name": "Fresh Kitchen Austin",
      "threat_level": "medium",
      ...
    },
    ... (4-8 total)
  ]
  Plus: "unfilled_gaps": ["B2B corporate model", "Lunch-only affordable tier", ...]
  ↓
Post-process:
  - Validate threat_level in {low, medium, high}
  - Sort by threat_level (high first)
  - Cap at 8 competitors
  ↓
Display: Threat matrix, unfilled gaps become strategy
```

**Key Logic:**
- Competitor gaps become your opportunities
- Threat level guides competitive positioning
- Local competitors are usually higher threat than national

---

### ROOT CAUSE (Strategic Analysis)

**Logic Flow:**
```
Input: Competitor gaps + customer pain + market data + root causes identified
  ↓
No search - pure strategic thinking
  ↓
Send to LLM:
  "You found 3 competitive gaps. WHY hasn't anyone solved them?
   Give 3-5 structural/economic/regulatory reasons, not just 'nobody thought of it'."
  ↓
LLM returns:
  [
    {
      "title": "Supplier relationship lock-in",
      "explanation": "Established brands have exclusive farm partnerships...",
      "your_move": "Partner directly with CSA suppliers instead of distributors",
      "difficulty": "medium"
    },
    {
      "title": "Delivery logistics complexity",
      "explanation": "Austin sprawl makes 3rd-party delivery expensive (30% cut)...",
      "your_move": "Start with 1 zip code, use hybrid direct + Doordash",
      "difficulty": "easy"
    },
    ... (3-5 total)
  ]
  ↓
Post-process:
  - Validate difficulty in {easy, medium, hard}
  - Sort by difficulty (easy first - quick wins)
  - Ensure each has actionable "your_move"
  ↓
Display: Accordion with strategies
```

**Key Logic:**
- Easy causes → implement first (quick wins)
- Difficult causes → long-term strategy/hiring
- "Your move" is your competitive advantage
- Answers the question: "Why can I succeed where others failed?"

---

### COSTS (Preview)

**Logic Flow:**
```
Input: Business type + location
  ↓
No search - LLM knowledge of commercial rates
  ↓
Send to LLM:
  "Estimate launch costs for meal prep delivery in Austin, TX"
  ↓
LLM returns:
  {
    "total_range": {"min": 45000, "max": 85000},
    "breakdown": [
      {"category": "Real Estate", "min": 10000, "max": 20000},
      {"category": "Equipment", "min": 15000, "max": 30000},
      {"category": "Permits & Legal", "min": 5000, "max": 8000},
      {"category": "Initial Operations", "min": 15000, "max": 27000}
    ],
    "note": "Kitchen rental is the biggest variable - $5-10k/mo downtown vs $2-3k/mo suburbs"
  }
  ↓
Display: Cost breakdown + cost driver callout
```

**Key Logic:**
- This is a "preview" - detailed breakdown is in TAB 4 (SETUP)
- Cost driver helps inform tier selection in SETUP
- Budget estimate feeds into team/timeline planning

---

## USER INTERACTION: How User Controls the Tab

### Initial Page Load

```
┌─────────────────────────────────────────────────────────┐
│ ANALYZE - Deep Market Analysis                     (3/5) │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Tab Navigation:                                        │
│  [◯ OPPORTUNITY]  [◯ CUSTOMERS]  [◯ COMPETITORS]       │
│  [◯ ROOT CAUSE]   [◯ COSTS]                            │
│                                                         │
│  (Nothing selected yet - waiting for user click)       │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  [Continue to SETUP] [Save to Dashboard] [Export PDF]  │
└─────────────────────────────────────────────────────────┘
```

### User Clicks "OPPORTUNITY"

```
┌─────────────────────────────────────────────────────────┐
│ ANALYZE - Deep Market Analysis                     (3/5) │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Tab Navigation:                                        │
│  [✓ OPPORTUNITY]  [◯ CUSTOMERS]  [◯ COMPETITORS]       │
│  [◯ ROOT CAUSE]   [◯ COSTS]                            │
│                                                         │
│  ───────────────────────────────────────────────────    │
│  OPPORTUNITY - Total Addressable Market                 │
│  ───────────────────────────────────────────────────    │
│                                                         │
│  🔄 Searching market data... analyzing TAM/SAM/SOM      │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  [Continue to SETUP] [Save to Dashboard] [Export PDF]  │
└─────────────────────────────────────────────────────────┘
```

### After 5-10 seconds (Results Load)

```
┌─────────────────────────────────────────────────────────┐
│ ANALYZE - Deep Market Analysis                     (3/5) │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Tab Navigation:                                        │
│  [✓ OPPORTUNITY]  [◯ CUSTOMERS]  [◯ COMPETITORS]       │
│  [◯ ROOT CAUSE]   [◯ COSTS]                            │
│                                                         │
│  ───────────────────────────────────────────────────    │
│  OPPORTUNITY - Total Addressable Market                 │
│  ───────────────────────────────────────────────────    │
│                                                         │
│  TAM (Total Addressable Market)                         │
│  ┌───────────────────────────────────┐                 │
│  │        💰 $150M                    │                 │
│  │                                   │                 │
│  │ Based on Austin metro population  │  ✅ HIGH CONF  │
│  │ and meal prep industry growth.    │                 │
│  └───────────────────────────────────┘                 │
│                                                         │
│  SAM (Serviceable Available Market)                     │
│  ┌───────────────────────────────────┐                 │
│  │        💚 $45M                     │                 │
│  │                                   │  ✅ HIGH CONF  │
│  │ Busy professionals 25-45, income  │                 │
│  │ spending $300-500/mo on dining.   │                 │
│  └───────────────────────────────────┘                 │
│                                                         │
│  SOM (Serviceable Obtainable Market - Year 1)          │
│  ┌───────────────────────────────────┐                 │
│  │        💛 $2.5M                    │                 │
│  │                                   │  ⚠️ MED CONF  │
│  │ Realistic target for 1 location   │                 │
│  │ in downtown Austin.               │                 │
│  └───────────────────────────────────┘                 │
│                                                         │
│  FUNNEL VISUALIZATION:                                 │
│  Population: 1,000,000                                 │
│      ↓ (50% aware)                                     │
│  Aware: 500,000                                        │
│      ↓ (50% interested)                                │
│  Interested: 250,000                                   │
│      ↓ (40% willing to try)                            │
│  Willing to Try: 100,000                               │
│      ↓ (50% repeat customers)                          │
│  Repeat Customers: 50,000 ← Your realistic market      │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  [Continue to SETUP] [Save to Dashboard] [Export PDF]  │
└─────────────────────────────────────────────────────────┘
```

### User Clicks "CUSTOMERS" While OPPORTUNITY Showing

```
┌─────────────────────────────────────────────────────────┐
│ ANALYZE - Deep Market Analysis                     (3/5) │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Tab Navigation:                                        │
│  [✓ OPPORTUNITY]  [✓ CUSTOMERS]  [◯ COMPETITORS]       │
│  [◯ ROOT CAUSE]   [◯ COSTS]                            │
│                                                         │
│  ───────────────────────────────────────────────────    │
│  CUSTOMERS - Segmentation Analysis                     │
│  ───────────────────────────────────────────────────    │
│                                                         │
│  🔄 Analyzing customer segments...                      │
│                                                         │
│  (OPPORTUNITY section still visible above - user can    │
│   scroll up to review, or scroll down to see new data) │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  [Continue to SETUP] [Save to Dashboard] [Export PDF]  │
└─────────────────────────────────────────────────────────┘
```

### After 3-5 seconds (CUSTOMERS Results Load)

```
SEGMENT 1
┌────────────────────────────────────┐
│ 💼 Busy Professionals              │
│ Pain Intensity: ❤️❤️❤️❤️❤️ 9/10   │
│                                    │
│ Population: 25,000 in Austin area  │
│ Primary need: Time-saving + health │
│ Spending: $300-500/month on dining │
│                                    │
│ Where to find:                     │
│ • LinkedIn (target by location)    │
│ • Whole Foods (health-conscious)   │
│ • Corporate gyms (fitness centers) │
│ • Tech offices downtown Austin     │
└────────────────────────────────────┘

SEGMENT 2
┌────────────────────────────────────┐
│ 🏃 Fitness Enthusiasts             │
│ Pain Intensity: ❤️❤️❤️❤️❤️❤️❤️ 7/10  │
│                                    │
│ Population: 18,000 in Austin area  │
│ Primary need: Macro nutrition info │
│ Spending: $400-600/month on fitness│
│                                    │
│ Where to find:                     │
│ • Planet Fitness, CrossFit boxes   │
│ • Reddit r/fitness, MyFitnessPal   │
│ • Nutrition tracking apps          │
└────────────────────────────────────┘

(Can scroll to see all 4 segments)
```

### User Can Click Any Section In Any Order

**Allowed flows:**
- ✅ OPPORTUNITY → COSTS → CUSTOMERS → ROOT CAUSE → COMPETITORS (any order)
- ✅ COMPETITORS → OPPORTUNITY (no wait between)
- ✅ Just click COSTS and skip the others entirely
- ✅ Click same section twice (loads from cache or fresh data)

**State persists:**
- Sections remain visible/expanded as user clicks new sections
- Can compare (scroll back to OPPORTUNITY while viewing CUSTOMERS)
- No sections auto-collapse (user controls everything)

---

## Key User Interactions

### 1. Click to Load Section
```
User clicks tab → Section enters "loading" state → LLM/search runs → Results render
No modal, no popups - everything inline
```

### 2. Expand/Collapse Details
```
Each insight/segment/competitor has expandable details:
[▶ Competitor Name] → click → [▼ Competitor Name with full details shown]
```

### 3. Switch Sections While Loading
```
Clicking COMPETITORS while OPPORTUNITY is still loading:
- OPPORTUNITY continues loading in background
- COMPETITORS starts loading
- Both eventually display
- No interference
```

### 4. Error Recovery
```
If COMPETITORS section fails:
┌──────────────────────────────────┐
│ ⚠️ COMPETITORS Section            │
│                                  │
│ Error: Unable to fetch data      │
│ (LLM unavailable)                │
│                                  │
│ [Retry] [Skip]                   │
└──────────────────────────────────┘

Other sections unaffected - continue using
```

### 5. Save & Export
```
[Save to Dashboard] → Stores all completed sections to database
[Export PDF] → Queues all sections for PDF generation
Both work regardless of which sections completed
```

---

## Navigation Flow

### Before ANALYZE Tab
```
TAB 1 (DECOMPOSE) → TAB 2 (DISCOVER) → TAB 3 (ANALYZE)
All sequential
```

### During ANALYZE Tab
```
User can:
1. Click any section in any order
2. Switch between ANALYZE and TAB 4 (SETUP) - both run in parallel
3. Spend 5 min on ANALYZE sections, then switch to SETUP tier selection
4. Come back to ANALYZE later
```

### After ANALYZE Tab
```
ANALYZE (completed sections saved) → TAB 5 (VALIDATE)
User continues when ready
```

---

## Loading States Explained

### Section Loading
```
┌─────────────────────────┐
│ 🔄 OPPORTUNITY         │
│                         │
│ Searching market data.. │ ← spinner + text
│ ~5 seconds              │
└─────────────────────────┘
```

### Section Loaded
```
┌─────────────────────────┐
│ ✅ OPPORTUNITY          │
│                         │
│ [Full results display]  │
└─────────────────────────┘
```

### Section Error
```
┌─────────────────────────┐
│ ⚠️ OPPORTUNITY          │
│                         │
│ Failed to load          │ ← error state
│ [Retry] [Skip]          │
└─────────────────────────┘
```

---

## Important UX Principles

### 1. **Non-Blocking Design**
- No section prevents progress through others
- One failure doesn't block the tab
- Can move to next tab even with incomplete sections

### 2. **User Control**
- User chooses which sections matter
- Not forced to complete all 5
- Can focus on 1-2 sections most relevant to their idea

### 3. **Transparency**
- Clear loading indicators
- Error messages explain why something failed
- Confidence levels show data quality

### 4. **Inline Results**
- No popups/modals
- Everything on same page
- Scroll to see all sections
- Sections don't push each other off-screen

### 5. **Persistence**
- Completed sections stay visible
- Can compare sections (scroll between them)
- All data saved to database when user clicks "Save"

---

## Summary: ANALYZE Tab Execution

```
┌──────────────────────────────────────────────────────────┐
│ User enters ANALYZE tab                                  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│ User clicks section (e.g., OPPORTUNITY)                 │
│         ↓                                                │
│ Backend: Fetch search data + call LLM in parallel       │
│         ↓                                                │
│ 5-15 seconds later: Results display                     │
│         ↓                                                │
│ User can:                                                │
│  • Click another section (all sections work independently)│
│  • Switch to TAB 4 (SETUP) - both run in parallel        │
│  • Scroll to compare sections                            │
│  • Click same section again to refresh                   │
│         ↓                                                │
│ When ready: [Save to Dashboard] or [Continue to SETUP]   │
│         ↓                                                │
│ All completed sections saved to database                │
│                                                          │
└──────────────────────────────────────────────────────────┘
```
