# VALIDATE Tab: Design & Functionality

## Overview

The VALIDATE tab has **2 distinct parts**:

### Part 1: VALIDATION TOOLKIT
**What it generates:** Reusable materials to test the business idea
- Landing page headline + benefits + CTA
- Customer survey with questions
- WhatsApp message templates
- Community recommendations (Reddit, Discord, etc)
- Scorecard with validation targets

### Part 2: EXPERIMENT TRACKING
**What it tracks:** Results from running validation experiments
- Log experiments (date, methods used, metrics collected)
- Track 6 key metrics per experiment
- AI-generated verdict: GO | PIVOT | KILL
- History of all experiments

---

## Part 1: Validation Toolkit

### Current Status: ✅ IMPLEMENTED

**Endpoint:** `POST /api/generate-validation`

**Input:**
```python
{
  "decomposition": {...},      # business type, location, customers
  "insight": {...},             # top pain point
  "channels": ["landing_page", "survey", "whatsapp", "communities", "scorecard"],
  "analysis_context": {...},    # ANALYZE tab data (SOM, gaps, moves)
  "setup_context": {...}        # SETUP tab data (cost tiers, timeline)
}
```

**Output: ValidateResponse**

#### 1. Landing Page
```json
{
  "landing_page": {
    "headline": "Skip the 15-minute wait. Get cold juice delivered in 2 hours.",
    "subheadline": "Premium organic juice subscription for busy professionals",
    "benefits": [
      "Fresh cold-pressed juice delivered to your office",
      "Choose from 10+ organic blends",
      "Cancel anytime, no commitment",
      "First bottle free"
    ],
    "cta_text": "Join the waitlist",
    "social_proof_quote": "\"Finally, a juice delivery that gets me.\" - Sarah, SF"
  }
}
```

**Data Sources:**
- Headline: From ROOT CAUSES "your_move" + CUSTOMERS pain language
- Benefits: From CUSTOMERS "primary_need" + SETUP "unfilled_gaps"
- CTA: Standard (Join waitlist)
- Social proof: Generated from DISCOVER evidence quotes

#### 2. Survey
```json
{
  "survey": {
    "title": "Quick Survey: Cold Juice Delivery",
    "questions": [
      {
        "number": 1,
        "question": "How often do you buy juice?",
        "type": "multiple_choice",
        "options": ["Daily", "3-4x/week", "1-2x/week", "Less often"]
      },
      {
        "number": 2,
        "question": "What's preventing you from buying more?",
        "type": "open_text",
        "options": null
      },
      {
        "number": 3,
        "question": "Would you switch to a delivery service?",
        "type": "yes_no",
        "options": ["Yes", "No", "Maybe"]
      },
      {
        "number": 4,
        "question": "Price you'd pay per bottle?",
        "type": "price",
        "options": ["$5-7", "$8-10", "$11-15", "$16+"]
      }
    ]
  }
}
```

**Data Sources:**
- Questions: Generated from ROOT CAUSES + CUSTOMERS pain + COMPETITORS pricing
- Question types: Based on what you need to validate
- Options: From market research (DISCOVER evidence)

#### 3. WhatsApp Message
```json
{
  "whatsapp_message": {
    "message": "Hey! 👋 We're launching premium cold-pressed juice delivery in SF next month. Get your first bottle free + skip the 15-min juice bar wait. Interested? [Link]",
    "tone": "casual"
  }
}
```

**Data Sources:**
- Message: From pain language + CUSTOMERS segment tone
- Tone: Casual/professional based on target segment

#### 4. Communities
```json
{
  "communities": [
    {
      "name": "r/fitness",
      "type": "reddit",
      "url": "https://reddit.com/r/fitness",
      "description": "700K fitness enthusiasts discuss nutrition",
      "why_useful": "Your primary customer segment (fitness = health conscious)",
      "posting_rules": "No direct links. Start conversation, offer value first."
    },
    {
      "name": "r/sanfrancisco",
      "type": "reddit",
      "url": "https://reddit.com/r/sanfrancisco",
      "description": "100K SF locals discussing life in the city",
      "why_useful": "Geographic validation - test demand in your target market",
      "posting_rules": "Follow subreddit rules. Be authentic."
    },
    {
      "name": "Nextdoor (SF neighborhoods)",
      "type": "nextdoor",
      "url": "https://nextdoor.com",
      "description": "Neighborhood-level hyper-local community",
      "why_useful": "Test with your literal neighbors (geographic)",
      "posting_rules": "Nextdoor is service-focused. Market naturally."
    }
  ]
}
```

**Data Sources:**
- Communities: From DECOMPOSE "subreddits" + target customer demographics
- Why useful: Explanation of relevance to business
- Posting rules: Generated based on community type

#### 5. Scorecard
```json
{
  "scorecard": {
    "validation_targets": [
      {
        "metric": "Waitlist Signups",
        "target": 500,
        "rationale": "Based on 2% click-through from 25K potential customers in SF"
      },
      {
        "metric": "Survey Completions",
        "target": 100,
        "rationale": "20% completion rate from waitlist (industry standard)"
      },
      {
        "metric": "Would You Switch (%)",
        "target": 70,
        "rationale": "Need 70%+ to prove strong demand (vs 50% for weak signal)"
      },
      {
        "metric": "Price Tolerance",
        "target": 12,
        "rationale": "Average of $10-14 range based on DISCOVER willingness-to-pay"
      },
      {
        "metric": "Community Engagement",
        "target": 50,
        "rationale": "50+ upvotes/comments shows community validation"
      },
      {
        "metric": "Reddit Upvotes",
        "target": 100,
        "rationale": "100+ upvotes on Reddit validates problem/solution fit"
      }
    ]
  }
}
```

**Data Sources:**
- Targets: Derived from OPPORTUNITY SOM, CUSTOMERS segments
- Rationale: Explained with market math

---

## Part 2: Validation Experiment Tracking

### Current Status: ⚠️ PARTIALLY IMPLEMENTED

**What Exists:**
- ✅ Schemas defined (ValidationExperimentResponse, etc)
- ✅ Metrics structure (6 KPIs)
- ✅ Verdict logic (GO | PIVOT | KILL)
- ❌ API endpoints (CRUD for experiments)
- ❌ Verdict calculation logic
- ❌ Frontend UI

### Validation Experiment Model

**6 Key Metrics:**
```python
{
  "waitlist_signups": 150,           # People who signed up
  "survey_completions": 45,          # People who filled survey
  "would_switch_rate": 75.5,         # % who said "Yes I'd switch"
  "price_tolerance_avg": 11.50,      # Average price they'd pay
  "community_engagement": 25,        # Sum of upvotes/comments
  "reddit_upvotes": 85               # Upvotes on Reddit posts
}
```

### Verdict Logic (GO | PIVOT | KILL)

**Algorithm:**
```python
def calculate_verdict(experiment, scorecard):
    """
    GO:    Met 4+ targets, 70%+ would switch, price >= $10
    PIVOT: Met 2-3 targets, 40-70% would switch, price $8-10
    KILL:  Met <2 targets, <40% would switch, price <$8
    """

    met_targets = 0
    metrics = [
        ("waitlist_signups", experiment.waitlist_signups >= scorecard.waitlist_target),
        ("survey_completions", experiment.survey_completions >= scorecard.survey_target),
        ("would_switch", experiment.would_switch_rate >= scorecard.switch_target),
        ("price_tolerance", experiment.price_tolerance >= scorecard.price_target),
        ("community", experiment.community_engagement >= scorecard.community_target),
        ("reddit", experiment.reddit_upvotes >= scorecard.reddit_target),
    ]

    met_targets = sum(1 for _, met in metrics if met)

    if met_targets >= 4 and experiment.would_switch_rate >= 70 and experiment.price_tolerance >= 10:
        return "GO"
    elif met_targets >= 2 and 40 <= experiment.would_switch_rate <= 70 and 8 <= experiment.price_tolerance <= 10:
        return "PIVOT"
    else:
        return "KILL"
```

**Example:**
```json
{
  "experiment_id": "exp_001",
  "idea_id": "idea_123",
  "methods": ["landing_page", "reddit"],
  "metrics": {
    "waitlist_signups": 320,
    "survey_completions": 78,
    "would_switch_rate": 82,
    "price_tolerance": 12.50,
    "community_engagement": 45,
    "reddit_upvotes": 120
  },
  "verdict": "GO",
  "reasoning": "Met 5/6 targets. 82% would switch. Price tolerance $12.50 > $12 target. Strong demand signal."
}
```

---

## User Experience Flow

### VALIDATE Tab UI (Mockup)

```
┌─────────────────────────────────────────────────────┐
│ VALIDATE: Test Your Idea                            │
├─────────────────────────────────────────────────────┤
│
│ Section 1: VALIDATION TOOLKIT
│ ┌─────────────────────────────────────────────────┐
│ │ Download your validation materials:             │
│ │                                                  │
│ │ [1] Landing Page (Headline + Benefits)         │
│ │     "Skip the 15-min wait. Juice in 2 hours."  │
│ │     [Download] [Copy]                          │
│ │                                                  │
│ │ [2] Survey (7 questions)                        │
│ │     "How often do you buy juice?"               │
│ │     [Download as PDF] [Embed Link]              │
│ │                                                  │
│ │ [3] WhatsApp Template                           │
│ │     "Hey! We're launching juice delivery..."   │
│ │     [Copy to clipboard]                         │
│ │                                                  │
│ │ [4] Community Targets (5 communities)           │
│ │     r/fitness (700K members)                    │
│ │     r/sanfrancisco (100K members)               │
│ │     Nextdoor SF                                 │
│ │     [View all] [Copy posting guidelines]        │
│ │                                                  │
│ │ [5] Validation Scorecard (6 targets)            │
│ │     Waitlist Signups: Target 500                │
│ │     Survey Completions: Target 100              │
│ │     Would Switch: Target 70%                    │
│ │     Price Tolerance: Target $12                 │
│ │     Community Engagement: Target 50             │
│ │     Reddit Upvotes: Target 100                  │
│ │                                                  │
│ └─────────────────────────────────────────────────┘
│
│ Section 2: VALIDATION EXPERIMENTS
│ ┌─────────────────────────────────────────────────┐
│ │ Past Experiments:                               │
│ │ ┌───────────────────────────────────────────┐  │
│ │ │ [Experiment 1] - Feb 15, 2025 - PENDING  │  │
│ │ │ Methods: landing_page, reddit             │  │
│ │ │ Signups: 145 / Target: 500                │  │
│ │ │ Switch Rate: 68% / Target: 70%            │  │
│ │ │ [View Details] [Edit]                     │  │
│ │ └───────────────────────────────────────────┘  │
│ │                                                  │
│ │ ┌───────────────────────────────────────────┐  │
│ │ │ [Experiment 2] - Feb 22, 2025 - GO ✓     │  │
│ │ │ Methods: landing_page, survey, reddit     │  │
│ │ │ Signups: 520 / Target: 500                │  │
│ │ │ Switch Rate: 82% / Target: 70%            │  │
│ │ │ Reasoning: "Met 5/6 targets. Strong go."  │  │
│ │ │ [View Details]                            │  │
│ │ └───────────────────────────────────────────┘  │
│ │
│ │ + Log New Experiment
│ │   ┌───────────────────────────────────────────┐
│ │   │ Methods:                                  │
│ │   │ ☑ Landing Page  ☑ Survey  ☐ WhatsApp   │
│ │   │ ☑ Reddit  ☐ Discord  ☐ Nextdoor        │
│ │   │                                           │
│ │   │ Metrics:                                  │
│ │   │ Waitlist Signups: [           ]          │
│ │   │ Survey Completions: [        ]           │
│ │   │ Would Switch %: [            ]           │
│ │   │ Price Tolerance: $[          ]           │
│ │   │ Community Engagement: [      ]           │
│ │   │ Reddit Upvotes: [            ]           │
│ │   │                                           │
│ │   │ [Save & Get Verdict]                     │
│ │   └───────────────────────────────────────────┘
│ │
│ └─────────────────────────────────────────────────┘
│
└─────────────────────────────────────────────────────┘
```

---

## Data Sources

| Component | Sources | LLM? |
|-----------|---------|------|
| **Landing Page** | ROOT_CAUSES + CUSTOMERS + DISCOVER evidence | ✅ Yes |
| **Survey** | ROOT_CAUSES + CUSTOMERS + COMPETITORS | ✅ Yes |
| **WhatsApp** | CUSTOMERS tone + pain language | ✅ Yes |
| **Communities** | DECOMPOSE subreddits + customer demographics | ❌ No (predetermined) |
| **Scorecard** | OPPORTUNITY SOM + CUSTOMERS segments | ⚠️ Partial (heuristics) |
| **Experiment Tracking** | User input (manual logging) | ❌ No |
| **Verdict** | Scorecard targets + experiment metrics | ❌ No (deterministic) |

---

## Current Implementation Status

| Feature | Status | Details |
|---------|--------|---------|
| **Toolkit Generation** | ✅ Complete | Endpoint working, all 5 components |
| **Landing Page** | ✅ Done | Headline + benefits + CTA |
| **Survey** | ✅ Done | 7 questions, multiple types |
| **WhatsApp** | ✅ Done | Message template generation |
| **Communities** | ✅ Done | Recommended with posting rules |
| **Scorecard** | ✅ Done | 6 targets with rationale |
| **Experiment CRUD** | ❌ Missing | No API endpoints |
| **Verdict Logic** | ❌ Missing | Algorithm designed but not implemented |
| **Frontend UI** | ❌ Missing | No VALIDATE tab UI |
| **Experiment History** | ❌ Missing | No storage/retrieval |

---

## What's Missing (Frontend Work)

1. **Validation Toolkit Display**
   - Show generated materials
   - Download/copy buttons
   - Landing page preview

2. **Experiment Tracking**
   - Form to log new experiment
   - List past experiments
   - Verdict card (GO/PIVOT/KILL)
   - Scorecard tracking

3. **Dashboard Integration**
   - Save experiments to idea
   - Show validation status on idea card
   - Track validation progress

---

## Next Steps to Complete VALIDATE

### Backend (if needed)
1. Create `/api/experiments` endpoints:
   - `POST /api/ideas/{id}/experiments` - Log new experiment
   - `GET /api/ideas/{id}/experiments` - Get all experiments
   - `PATCH /api/experiments/{id}` - Update metrics
   - `DELETE /api/experiments/{id}` - Delete experiment

2. Implement verdict logic in service

3. Add database table for validation_experiments

### Frontend
1. Build VALIDATE tab UI (toolkit section)
2. Build experiment logging form
3. Build experiment history list
4. Wire to dashboard

---

## Example Flow

```
User in VALIDATE tab:
    ↓
1. Reads toolkit (landing page, survey, scorecard)
2. Downloads materials
3. Runs validation experiments:
   - Posts landing page on Reddit
   - Surveys customers
   - Checks WhatsApp response
4. Logs results: "500 signups, 82% would switch"
    ↓
System calculates: "GO ✓"
    ↓
User sees: "Strong demand signal. Proceed to launch."
```

