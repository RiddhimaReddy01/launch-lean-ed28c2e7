# VALIDATE Tab (TAB 5) - Complete Specification

## Quick Summary
The VALIDATE tab generates a **demand validation toolkit** - everything you need to prove customers want your product BEFORE building it. Uses accumulated context from all 4 prior modules.

---

## FUNCTIONALITY: What the Tab Does

### 5 Outputs Generated in Single LLM Call

| Component | Purpose | Output |
|-----------|---------|--------|
| **Landing Page** | Capture early demand | Headline, subheadline, benefits, CTA, social proof quote |
| **Survey** | Validate assumptions | 7 structured questions to ask early customers |
| **WhatsApp Message** | Reach local communities | Casual, shareable text for group chats |
| **Communities** | Find your audience | 10 platforms/groups to share in (Facebook, Discord, Reddit, etc.) |
| **Scorecard** | Track validation progress | Targets: waitlist (50), survey responses (10), switch rate (60%), price tolerance ($X) |

### Single Call, Multiple Outputs
Unlike prior tabs (ANALYZE has 5 separate sections), VALIDATE generates ALL components in **one LLM call** (~5-8 seconds).

---

## LOGIC: How Validation Works

### Data Flow

```
Input from all 5 prior modules:
┌──────────────────────────────────────────────────────────┐
│ TAB 1 (DECOMPOSE)                                        │
│ - Business type: "meal prep delivery"                    │
│ - Location: Austin, TX                                   │
│ - Target customers: ["busy professionals"]               │
│                                                          │
│ TAB 2 (DISCOVER)                                         │
│ - Insight evidence/quotes: ["I don't have time..."]     │
│ - Source context: Reddit, Google search                  │
│                                                          │
│ TAB 3 (ANALYZE)                                          │
│ - Competitor gaps: ["No B2B model", "No affordable..."] │
│ - Root cause strategies: "Partner with CSA suppliers..." │
│ - Market SOM: $2.5M                                      │
│                                                          │
│ TAB 4 (SETUP)                                            │
│ - Cost tiers: $45k-85k (MID)                             │
│ - Timeline: 6 months to launch                           │
│                                                          │
└──────────────────────────────────────────────────────────┘
         ↓
   Data transformation (extracting key signals)
         ↓
   Single LLM call with all context
         ↓
   Validation toolkit generated
```

### 4-Stage Processing Pipeline

#### STAGE 1: Data Ingestion
```
Only NEW external data: Community discovery
- Build 3-5 community search queries from business type
- Example: "Austin meal prep groups", "fitness communities Austin", etc.
- Search via Serper (8 results per query)
- Get community info: name, size, engagement
```

#### STAGE 2: Data Cleaning
```
Clean community search results
- Extract valid communities (remove spam, dead links)
- Get: name, platform (facebook, discord, reddit, etc.), member count, link
- Keep top 15 for context
```

#### STAGE 3: Data Transformation
```
Extract key signals from prior modules:

1. Pain language extraction:
   - Get top 10 customer quotes from insight evidence
   - Extract insight title as pain phrase
   - These are used VERBATIM in landing page copy

2. Analysis summary (from TAB 3):
   - SOM estimate: "$2.5M"
   - Competitor gaps: "No B2B model"
   - Root cause counter-strategies
   - Primary customer segment

3. Setup summary (from TAB 4):
   - Cost tiers: "LEAN: $27k-68k, MID: $45k-85k, PREMIUM: $54k-153k"
   - Timeline: "Total 24 weeks"
```

#### STAGE 4: LLM Call
```
Single Groq LLM call with:
- System prompt (instructions for generating validation materials)
- User prompt (all context + pain language + analysis + setup + communities)
- Temperature: 0.6 (balanced creativity for copywriting)
- Max tokens: 4000 (enough for all 5 components)
- JSON mode: true

Output: Structured JSON with all 5 components
```

#### STAGE 5: Post-Processing
```
Validate and format output:
- Landing page: ensure 3-4 benefits, CTA text
- Survey: normalize question types (multiple_choice, scale, open_text, email, yes_no)
- WhatsApp: ensure [SURVEY_LINK] placeholder exists
- Communities: normalize platform names (facebook, discord, reddit, etc.)
- Scorecard: extract numbers from strings (e.g., "Above $45" → 45)
```

---

## DATA SOURCES: Where Validation Gets Its Inputs

### Input 1: DECOMPOSE (TAB 1)
```json
{
  "business_type": "meal prep delivery service",
  "location": {
    "city": "Austin",
    "state": "TX"
  },
  "target_customers": ["busy professionals", "health-conscious"],
  "search_queries": ["meal prep delivery Austin", ...]
}
```
**Used for:** Business context, location-specific validation

### Input 2: DISCOVER (TAB 2) - CRITICAL
```json
{
  "insights": [
    {
      "title": "Lack of time for meal prep on weekends",
      "evidence": [
        {
          "quote": "I don't have time to meal prep every weekend",
          "source": "reddit"
        },
        {
          "quote": "Working 50+ hours makes healthy eating impossible",
          "source": "google_search"
        }
      ]
    }
  ]
}
```
**Used for:** CUSTOMER PAIN LANGUAGE (copied verbatim into landing page)
- System prompt: "CRITICAL: Use EXACT pain language from quotes. Copy should sound like customers, not marketers."

### Input 3: ANALYZE (TAB 3)
```json
{
  "opportunity": {
    "som": {
      "formatted": "$2.5M",
      "value": 2500000
    }
  },
  "competitors": {
    "unfilled_gaps": [
      "No B2B corporate partnership model",
      "No affordable lunch-only tier",
      "Missing macro customization at premium pricing"
    ]
  },
  "rootcause": {
    "root_causes": [
      {
        "title": "Supplier relationship lock-in",
        "your_move": "Partner directly with CSA suppliers instead of distributors"
      }
    ]
  },
  "customers": {
    "segments": [
      {
        "name": "Busy Professionals",
        "primary_need": "Time-saving solution with healthy food"
      }
    ]
  }
}
```
**Used for:** Market context + strategic positioning

### Input 4: SETUP (TAB 4)
```json
{
  "cost_tiers": [
    {
      "tier": "LEAN",
      "total_range": {"min": 27000, "max": 68000}
    },
    {
      "tier": "MID",
      "total_range": {"min": 45000, "max": 85000}
    }
  ],
  "timeline": [
    {
      "phase": "VALIDATION",
      "weeks": 6
    }
  ]
}
```
**Used for:** Cost/timeline context (when should validation happen, budget constraints)

### Input 5: NEW Search Data (Community Discovery)
```
Run community search queries:
- "Austin meal prep delivery groups"
- "fitness enthusiast communities Austin"
- "busy professionals groups Austin"
- "entrepreneurship Austin groups"

Get 40 results (5 queries × 8 results)
Clean and extract top 15 communities
```

---

## LLM PROMPTS: Exact Instructions Sent to Groq

### System Prompt (validate_system)

```
Generate demand validation materials for a meal prep delivery service in Austin, TX.

CRITICAL: Use the EXACT pain language from the customer quotes provided. The landing page copy
should sound like the customers, not like a marketer.

Return JSON:
{
  "landing_page": {
    "headline": "Attention-grabbing headline using #1 pain point",
    "subheadline": "Promise the solution in one sentence",
    "benefits": ["3-4 bullet points using customer language"],
    "cta_text": "Action-oriented button text",
    "social_proof_quote": "A real quote from Module 1 evidence"
  },
  "survey": {
    "title": "Survey title",
    "questions": [
      {
        "number": 1,
        "question": "Question text",
        "type": "multiple_choice | scale | open_text | email | yes_no",
        "options": ["array of options if multiple_choice, null otherwise"]
      }
    ]
  },
  "whatsapp_message": {
    "message": "Casual, shareable message for local groups. Include [SURVEY_LINK] placeholder.",
    "tone_note": "Brief note on tone"
  },
  "communities": [
    {
      "name": "Community/group name",
      "platform": "facebook | discord | nextdoor | reddit | other",
      "member_count": "estimated count string or null",
      "rationale": "Why share here (1 sentence)",
      "link": "Direct link if known"
    }
  ],
  "scorecard": {
    "waitlist_target": number,
    "survey_target": 50,
    "switch_pct_target": 60,
    "price_tolerance_target": "Above $X (minimum viable price)",
    "paid_signups_target": 5,
    "ltv_cac_ratio_target": 3.0,
    "is_custom": false
  }
}

Generate exactly 7 survey questions in this order:
1. Frequency of current purchases
2. Current solution / where they go now
3. Biggest frustration (open text)
4. Willingness to switch (yes/no/maybe)
5. Price sensitivity (range options)
6. Location preference (multiple choice)
7. Email capture for launch updates
```

### User Prompt (validate_user)

```
Generate validation materials for:

Business: meal prep delivery service
Location: Austin, TX
Key insight: Lack of time for meal prep on weekends

CUSTOMER PAIN LANGUAGE (use these exact phrases in the landing page):
  - "Lack of time for meal prep on weekends"
  - "I don't have time to meal prep every weekend"
  - "Working 50+ hours makes healthy eating impossible"
  - "I'd pay premium for healthy meals delivered"

Market context:
Market SOM: $2.5M
Unfilled gaps: No B2B corporate model; No affordable lunch-only tier; Missing macro customization
Unfilled gaps: Supplier relationship lock-in - Partner directly with CSA suppliers
Primary segment: Busy Professionals (time-saving + healthy)

Launch plan context:
LEAN: $27k-68k
MID: $45k-85k
PREMIUM: $54k-153k
Total timeline: ~24 weeks

Communities available (find top 10 to share in):
  - Austin Entrepreneurs group (Facebook, 15,000+ members)
  - Busy Professionals Austin (LinkedIn, 8,000+ members)
  - r/Austin (Reddit, 400,000+ members)
  - Austin Health & Fitness groups (WhatsApp, Discord)
  - [Search results with more communities...]
```

### Key Prompt Principles

1. **"CRITICAL" instruction**: Use EXACT customer language (from DISCOVER)
2. **Contextual threading**: All 4 prior modules woven together
3. **Specific structure**: 7 survey questions in fixed order
4. **Community relevance**: Match communities to target customers
5. **Measurable targets**: Scorecard goals are testable

---

## OUTPUT: What Validation Generates

### Output 1: Landing Page

```json
{
  "landing_page": {
    "headline": "Stop wasting weekends on meal prep. Start eating healthy in minutes.",
    "subheadline": "Fresh, personalized meal deliveries for Austin professionals who refuse to sacrifice health for time.",
    "benefits": [
      "Macro-balanced meals delivered fresh to your door (no reheating frozen food)",
      "Customize every meal - dietary preferences, ingredient swaps, macro targets",
      "Save 5+ hours/week on shopping, cooking, cleanup",
      "Support local Austin farms + sustainable sourcing"
    ],
    "cta_text": "Join the waitlist - early access for $15/meal",
    "social_proof_quote": "I'd pay premium for healthy meals delivered. I just don't have time to meal prep."
  }
}
```

**Why these words?**
- "Stop wasting weekends" - directly from pain language
- "refusing to sacrifice health" - echoes insight
- Benefits use customer language, not marketing speak
- Quote is verbatim from DISCOVER insight evidence

### Output 2: Survey

```json
{
  "survey": {
    "title": "Quick survey: Your meal prep needs",
    "questions": [
      {
        "number": 1,
        "question": "How often do you currently buy prepared meals or use meal delivery?",
        "type": "scale",
        "options": null
      },
      {
        "number": 2,
        "question": "Where do you currently get your meals? (Select all that apply)",
        "type": "multiple_choice",
        "options": [
          "Cook at home",
          "Restaurant/takeout",
          "Existing meal prep delivery (Factor, Freshly, etc)",
          "Mix of everything"
        ]
      },
      {
        "number": 3,
        "question": "What's your biggest frustration with meal prep or eating healthy right now?",
        "type": "open_text",
        "options": null
      },
      {
        "number": 4,
        "question": "Would you switch to a local, personalized meal delivery service if it saved you 5+ hours/week?",
        "type": "yes_no",
        "options": ["Yes", "No", "Maybe"]
      },
      {
        "number": 5,
        "question": "What price would you pay per meal? (Austin market average: $12-18)",
        "type": "multiple_choice",
        "options": [
          "Under $12 (budget)",
          "$12-15 (reasonable)",
          "$15-18 (fair for quality)",
          "$18+ (worth it for customization)"
        ]
      },
      {
        "number": 6,
        "question": "How important is local sourcing from Austin-area farms?",
        "type": "scale",
        "options": null
      },
      {
        "number": 7,
        "question": "What's your email? (We'll notify you when we launch)",
        "type": "email",
        "options": null
      }
    ]
  }
}
```

**Survey Logic:**
- Q1: Frequency baseline
- Q2: Current alternatives (find competitors customers use)
- Q3: Pain points (validate DISCOVER insight)
- Q4: Willingness to switch (conversion signal)
- Q5: Price tolerance (critical for positioning)
- Q6: Differentiation signal (local sourcing from root cause)
- Q7: Email capture (build waitlist)

### Output 3: WhatsApp Message

```json
{
  "whatsapp_message": {
    "message": "Hey! 👋 Are you spending your entire weekend meal prepping, only to give up by Wednesday? 🍽️\n\nWe're building fresh, personalized meal delivery for Austin professionals who want healthy eating WITHOUT the stress.\n\nTake 2 min survey to help us build this right → [SURVEY_LINK]\n\nFirst 100 customers get $15/meal launch pricing 🎉",
    "tone_note": "Casual, personal, uses emoji, includes benefit + CTA + urgency"
  }
}
```

**Why this format?**
- No salesy language - sounds like friend
- Leads with pain ("spending entire weekend")
- Benefit clear ("WITHOUT the stress")
- CTA is low-friction ("2 min survey")
- Urgency: "first 100 customers"
- Includes [SURVEY_LINK] placeholder (user fills in their form URL)

### Output 4: Communities

```json
{
  "communities": [
    {
      "name": "Austin Entrepreneurs & Startups",
      "platform": "facebook",
      "member_count": "25,000+",
      "rationale": "Busy founders understand time scarcity. Early adopters for testing.",
      "link": "https://facebook.com/groups/austin-entrepreneurs"
    },
    {
      "name": "Busy Professionals Austin",
      "platform": "linkedin",
      "member_count": "12,000+",
      "rationale": "Direct match for target segment. High income, time-starved professionals.",
      "link": "https://linkedin.com/groups/busy-professionals-austin"
    },
    {
      "name": "r/Austin",
      "platform": "reddit",
      "member_count": "400,000+",
      "rationale": "Largest Austin community. Share in Daily Thread for feedback.",
      "link": "https://reddit.com/r/Austin"
    },
    {
      "name": "Austin Health & Fitness",
      "platform": "facebook",
      "member_count": "8,000+",
      "rationale": "Fitness-focused segment cares about macros & nutrition.",
      "link": "https://facebook.com/groups/austin-health-fitness"
    },
    {
      "name": "Austin Mom's Network",
      "platform": "facebook",
      "member_count": "15,000+",
      "rationale": "Time-starved segment. Care about family nutrition.",
      "link": "https://facebook.com/groups/austin-moms"
    },
    ... (5 more communities)
  ]
}
```

**Community Selection Logic:**
- Mix of platforms (Facebook, LinkedIn, Reddit)
- Match to target segment (busy professionals, fitness, parents)
- Provide direct links (user can paste WhatsApp message)
- Rationale explains why each is relevant

### Output 5: Scorecard

```json
{
  "scorecard": {
    "waitlist_target": 50,
    "survey_target": 10,
    "switch_pct_target": 60,
    "price_tolerance_target": 15.5,
    "paid_signups_target": 5,
    "ltv_cac_ratio_target": 3.0,
    "is_custom": false
  }
}
```

**Scorecard Metrics Explained:**

| Metric | Target | What It Means | How to Track |
|--------|--------|---------------|-------------|
| **waitlist_target** | 50 | Get 50 people on waitlist | Share WhatsApp message, collect survey responses |
| **survey_target** | 10 | Get 10 survey completions | Track survey form submissions |
| **switch_pct_target** | 60 | 60% say "yes" to switching | Q4: "Would you switch?" response rate |
| **price_tolerance_target** | $15.50 | Average price customers would pay | Q5: "What price per meal?" - take avg |
| **paid_signups_target** | 5 | Get 5 people to pre-pay | Start collecting deposits from top 5 |
| **ltv_cac_ratio_target** | 3.0 | Revenue/Acquisition cost ratio | Early KPI to track profitability |
| **is_custom** | false | Not a custom scorecard | False = using defaults |

---

## COMPLETE WORKFLOW: Step-by-Step

### What User Sees

```
┌────────────────────────────────────────────────────────┐
│ VALIDATE - Demand Validation Toolkit            (5/5) │
├────────────────────────────────────────────────────────┤
│                                                       │
│ 🔄 Generating validation materials...               │
│ (Analyzing all prior modules + finding communities) │
│                                                       │
├────────────────────────────────────────────────────────┤
│ [Go to ANALYZE] [Save to Dashboard] [Export PDF]     │
└────────────────────────────────────────────────────────┘
```

### After 5-8 seconds

```
┌────────────────────────────────────────────────────────┐
│ VALIDATE - Demand Validation Toolkit            (5/5) │
├────────────────────────────────────────────────────────┤
│                                                       │
│ SECTION 1: Landing Page                             │
│ ─────────────────────────────────────────────────   │
│                                                       │
│ Headline: "Stop wasting weekends on meal prep..."   │
│ Subheadline: "Fresh, personalized meals..."         │
│ [Benefits shown as copy blocks]                     │
│ CTA: "Join the waitlist - early access"             │
│ Social proof: "I'd pay premium for..."              │
│                                                       │
│ [Copy all] [Preview on mobile]                      │
│                                                       │
├────────────────────────────────────────────────────────┤
│
│ SECTION 2: Survey Template
│ ─────────────────────────────────────────────────   │
│
│ Title: "Quick survey: Your meal prep needs"         │
│ [7 questions displayed]                              │
│ Q1: Frequency (scale)                               │
│ Q2: Where do you get meals? (multiple choice)       │
│ ... (Q3-Q7)                                          │
│                                                       │
│ [Copy survey JSON] [Create Google Form]              │
│
├────────────────────────────────────────────────────────┤
│
│ SECTION 3: WhatsApp Message
│ ─────────────────────────────────────────────────   │
│
│ "Hey! 👋 Are you spending your entire weekend..."   │
│                                                       │
│ [Copy to clipboard] [Send to WhatsApp]               │
│
├────────────────────────────────────────────────────────┤
│
│ SECTION 4: Communities to Share In
│ ─────────────────────────────────────────────────   │
│
│ 1. Austin Entrepreneurs (Facebook, 25k members)      │
│    Rationale: Early adopters, understand time...     │
│                                                       │
│ 2. Busy Professionals Austin (LinkedIn, 12k)         │
│    Rationale: Direct match for target segment...     │
│                                                       │
│ ... (10 total)                                        │
│                                                       │
│ [Share WhatsApp message in these groups]             │
│
├────────────────────────────────────────────────────────┤
│
│ SECTION 5: Validation Scorecard
│ ─────────────────────────────────────────────────   │
│
│ Track your validation progress:                       │
│ ☐ Waitlist: 0/50                                    │
│ ☐ Survey responses: 0/10                            │
│ ☐ Switch rate: 0% (target 60%)                      │
│ ☐ Avg price tolerance: $0 (target $15.50)           │
│ ☐ Pre-paid signups: 0/5                             │
│                                                       │
│ [Print scorecard] [Share with team]                  │
│
├────────────────────────────────────────────────────────┤
│ [Save to Dashboard] [Export PDF] [Continue]          │
└────────────────────────────────────────────────────────┘
```

---

## Data Source Dependencies

### What if Prior Modules Failed?

```
If TAB 2 (DISCOVER) missing insights:
  → No pain language extracted
  → Landing page less customer-centric
  → Still generates materials using business type context

If TAB 3 (ANALYZE) missing competitors:
  → No unfilled gaps for communities
  → Still selects communities based on business type

If TAB 4 (SETUP) missing timeline:
  → No timeline context
  → Validation materials still generated
  → Can't estimate timeline for validation phase

If community search fails:
  → Still generates landing page, survey, WhatsApp, scorecard
  → Communities list is empty or generic
```

**Key Insight:** VALIDATE is resilient - can work with partial data. But most powerful when all 4 prior modules complete.

---

## Key Features

### 1. "Use EXACT Pain Language"
- System prompt explicitly says: "Use EXACT pain language from quotes"
- Landing page copy pulls verbatim from customer evidence
- Makes copy authentic (sounds like customers, not marketers)

### 2. Single Integrated Call
- All 5 components generated in one LLM call (~5-8 seconds)
- Faster than running 5 separate generations
- Context shared across components (consistency)

### 3. Community-Based Validation
- Finds 10 communities to share in
- Matches communities to target segment
- Provides direct links + WhatsApp message for sharing
- Enables quick, low-cost customer outreach

### 4. Measurable Scorecard
- 7 specific, testable metrics
- Can be tracked in spreadsheet/dashboard
- Shows progress from landing page → waitlist → survey → paid signups
- ltv_cac_ratio: Shows unit economics (most important metric)

### 5. Multi-Format Outputs
- Landing page (for website/email)
- Survey (for Google Forms/Typeform)
- WhatsApp message (for community sharing)
- Communities list (action items)
- Scorecard (tracking template)

---

## Integration Points

### Input Flow
```
Decompose → Discover → Analyze → Setup → Validate
   ↓         ↓         ↓         ↓        ↓
  (Context is threaded through all stages)
```

### Output Flow
```
Validate → Dashboard (save idea)
        → PDF Export (complete report)
        → Scorecard (tracking sheet)
```

### Next Steps After Validate
1. Post WhatsApp message in communities
2. Track responses in scorecard
3. If 60%+ say "yes" to switching → Go to Market
4. If 60%+ say "no" → Pivot business model/positioning
5. Return to TAB 3 (ANALYZE) to find better gaps

---

## Performance Notes

- **Community search**: 2-3 seconds (Serper API)
- **LLM generation**: 3-5 seconds (Groq call)
- **Post-processing**: <500ms
- **Total**: ~5-8 seconds per call
- No caching (validation is context-dependent on prior selections)

---

## Testing Checklist

- ✓ Landing page uses customer pain language (verbatim from DISCOVER)
- ✓ Headline references insight title
- ✓ Benefits use customer language, not marketing speak
- ✓ Social proof quote is from evidence
- ✓ Survey has exactly 7 questions in prescribed order
- ✓ Q1: Frequency (scale), Q2: Alternatives (multiple choice), Q3: Frustration (open), Q4: Switch (yes/no), Q5: Price (multiple choice), Q6: Differentiation (scale), Q7: Email
- ✓ WhatsApp message includes [SURVEY_LINK] placeholder
- ✓ Communities are relevant to target segment
- ✓ Communities have valid platform names (facebook, discord, reddit, etc.)
- ✓ Scorecard metrics are numeric (not strings)
- ✓ Price tolerance extracted from string correctly (e.g., "Above $45" → 45)
- ✓ All 5 components present even if some prior modules incomplete
- ✓ Save to Dashboard works
- ✓ Export PDF includes all 5 validation components
- ✓ Mobile responsive: All copy blocks readable
- ✓ No console errors
