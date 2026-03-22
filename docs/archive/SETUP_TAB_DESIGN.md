# SETUP Tab: Design & Current State

## Current Status

### What Exists (Backend)
✅ **Schema defined** in `models.py`:
```python
class SetupResponse(BaseModel):
    cost_tiers: list[CostTier]       # Different pricing models
    suppliers: list[Supplier]         # Recommended vendors
    team: list[TeamRole]             # Hiring needs
    timeline: list[TimelinePhase]    # Launch roadmap
```

✅ **Database fields** in ideas table:
```sql
setup: Optional[dict]  -- stores SetupResponse
has_setup: bool        -- tracks if completed
```

❌ **NO API endpoint** - `/api/setup` doesn't exist yet
❌ **NO logic** - Nothing generates SetupResponse data

---

## What SETUP Tab SHOULD Be

### 1. Purpose
Convert ANALYZE outputs (ROOT CAUSES, COSTS) into **actionable launch plan**:

```
ANALYZE outputs:
  ├─ ROOT CAUSES [3-5 core problems]
  ├─ COSTS [breakdown by category]
  └─ CUSTOMERS [market segments]

        ↓↓↓ (SETUP synthesizes) ↓↓↓

SETUP outputs:
  ├─ Cost Tiers [3 pricing scenarios: lean/mid/premium]
  ├─ Suppliers [recommended vendors for each tier]
  ├─ Team [roles needed, salary ranges, priority]
  └─ Timeline [12-month roadmap with milestones]
```

---

## What User SEES: SETUP Tab UI

### Section 1: Cost Tiers (3 Models)

User sees 3 cards side-by-side:

```
┌─────────────────────────────────────────────────────────────┐
│ COST TIERS: Choose Your Launch Model                         │
├─────────────────────────────────────────────────────────────┤
│
│  LEAN 💪                MID 🎯                PREMIUM 🚀
│  $30-50k               $75-100k              $150-200k
│
│  • No-code platform    • Custom app          • Full team
│  • 1-2 freelancers     • 1 FTE engineer      • 2-3 FTEs
│  • 4 months            • 6 months            • 8 months
│  • High founder load   • Balanced            • Team-focused
│
│  [Choose Lean]         [Choose Mid]          [Choose Premium]
│
└─────────────────────────────────────────────────────────────┘
```

**What's in each tier:**
- Total cost range ($min-$max)
- Engineering approach (no-code vs custom)
- Team size
- Timeline
- Philosophy (speed vs quality)

---

### Section 2: Suppliers (Recommended Vendors)

For selected tier, show recommended vendors:

```
┌─────────────────────────────────────────────────────────────┐
│ SUPPLIERS: Recommended for MID Tier                          │
├─────────────────────────────────────────────────────────────┤
│
│ [Category: Engineering]
│ ┌─────────────────────────────────────────────────────────┐
│ │ Upwork (Freelance)                                      │
│ │ Recommended for: Finding contractors fast ($30-50/hr)   │
│ │ [Get link →]                                            │
│ ├─────────────────────────────────────────────────────────┤
│ │ Y Combinator Startup School (Mentorship)                │
│ │ Recommended for: Go-to-market advice + network          │
│ │ [Get link →]                                            │
│ └─────────────────────────────────────────────────────────┘
│
│ [Category: Marketing]
│ ┌─────────────────────────────────────────────────────────┐
│ │ Google Local Services Ads                               │
│ │ Recommended for: $X/month for plumber/HVAC markets      │
│ │ [Get link →]                                            │
│ └─────────────────────────────────────────────────────────┘
│
│ [Category: Legal]
│ ┌─────────────────────────────────────────────────────────┐
│ │ Stripe Atlas ($500 + filing)                            │
│ │ Recommended for: Quick entity formation                 │
│ │ [Get link →]                                            │
│ └─────────────────────────────────────────────────────────┘
│
└─────────────────────────────────────────────────────────────┘
```

**For each supplier:**
- Category (Engineering, Marketing, Legal, etc)
- Why recommended (specific to their business)
- Link to website

---

### Section 3: Team (Hiring Plan)

Show timeline of hiring needs:

```
┌─────────────────────────────────────────────────────────────┐
│ TEAM: Hiring Roadmap (MID Tier)                             │
├─────────────────────────────────────────────────────────────┤
│
│ MONTH 1-3: Founder + Freelancers
│ ┌─────────────────────────────────────────────────────────┐
│ │ [1] Backend Engineer (Contract) - $30-40/hr             │
│ │     Priority: MUST_HAVE                                 │
│ │     Duration: 3 months                                  │
│ │     Where: Upwork, Toptal                              │
│ │
│ │ [2] Designer (Contract) - $25-35/hr                     │
│ │     Priority: NICE_TO_HAVE                              │
│ │     Duration: 2 months                                  │
│ │     Where: Dribbble, 99designs                         │
│ └─────────────────────────────────────────────────────────┘
│
│ MONTH 4-6: First Hire
│ ┌─────────────────────────────────────────────────────────┐
│ │ [1] Full-Time Engineer - $80-120k/year                  │
│ │     Priority: MUST_HAVE                                 │
│ │     Type: FTE (Full-Time Employee)                      │
│ │     When: Hire by Month 4                              │
│ └─────────────────────────────────────────────────────────┘
│
│ MONTH 7-12: Team Scaling
│ ┌─────────────────────────────────────────────────────────┐
│ │ [1] Operations Manager - $60-80k/year                   │
│ │     Priority: NICE_TO_HAVE                              │
│ │     When: Month 7 if revenue >$X                        │
│ └─────────────────────────────────────────────────────────┘
│
└─────────────────────────────────────────────────────────────┘
```

**For each role:**
- Title
- Salary range (for FTE)
- Priority (MUST_HAVE vs NICE_TO_HAVE)
- Type (Contract, FTE, Advisory)
- When to hire
- Where to find

---

### Section 4: Timeline (12-Month Roadmap)

Gantt-style timeline:

```
┌─────────────────────────────────────────────────────────────┐
│ TIMELINE: 12-Month Launch Plan                              │
├─────────────────────────────────────────────────────────────┤
│
│ PHASE 1: VALIDATION (Months 1-2)
│ ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
│ Milestones:
│   ✓ Landing page live
│   ✓ 100 waitlist signups
│   ✓ 5 user interviews
│   ✓ Legal entity formed
│
│ PHASE 2: BUILD MVP (Months 3-5)
│ ░░░░████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
│ Milestones:
│   ✓ Core product built
│   ✓ 10 beta users testing
│   ✓ Payment processing live
│   ✓ Refine based on feedback
│
│ PHASE 3: LAUNCH (Months 6-7)
│ ░░░░░░░░████░░░░░░░░░░░░░░░░░░░░░░░░░░
│ Milestones:
│   ✓ Public launch
│   ✓ First 50 customers
│   ✓ First employee hired
│   ✓ Marketing campaign live
│
│ PHASE 4: SCALE (Months 8-12)
│ ░░░░░░░░░░░░████████░░░░░░░░░░░░░░░░░░
│ Milestones:
│   ✓ $X monthly recurring revenue
│   ✓ 200+ active customers
│   ✓ Expand to 2nd market
│   ✓ Team of 3
│
└─────────────────────────────────────────────────────────────┘
```

**For each phase:**
- Name (VALIDATION, BUILD, LAUNCH, SCALE)
- Duration (weeks)
- Key milestones
- Success criteria

---

## How SETUP Data is Generated

### Input Data (From ANALYZE)

```python
INPUT = {
    "root_causes": [
        {
            "title": "Long wait times",
            "difficulty": "easy",
            "your_move": "Build subscription + delivery"
        },
        {
            "title": "Supply chain gap",
            "difficulty": "medium",
            "your_move": "Partner with logistics provider"
        },
        {
            "title": "Premium pricing only",
            "difficulty": "hard",
            "your_move": "Offer tiered subscriptions"
        }
    ],
    "costs": {
        "total_range": {"min": 50000, "max": 100000},
        "breakdown": [
            {"category": "Engineering", "range": {"min": 20000, "max": 40000}},
            {"category": "Operations", "range": {"min": 5000, "max": 10000}},
            ...
        ]
    },
    "customers": [
        {"name": "Segment 1", "pain_intensity": 8, "spending_pattern": "$15-25/day"},
        ...
    ],
    "business_type": "Cold-pressed juice subscription",
    "location": {"city": "San Francisco", "state": "CA"}
}
```

### Output Generation Logic

**Step 1: Create 3 Cost Tiers**

```python
# LEAN: Use no-code tools, min freelancers
lean_tier = {
    "model": "LEAN",
    "total_range": {
        "min": INPUT["costs"]["total_range"]["min"] * 0.6,      # 60% of baseline
        "max": INPUT["costs"]["total_range"]["min"] * 0.8       # 80% of baseline
    },
    "philosophy": "Speed + founder effort, quality risk",
    "team_size": 1-2,
    "timeline": "4 months"
}

# MID: Balanced approach (baseline costs)
mid_tier = {
    "model": "MID",
    "total_range": INPUT["costs"]["total_range"],   # Use exact COSTS
    "philosophy": "Balanced speed, quality, team size",
    "team_size": 1,
    "timeline": "6 months"
}

# PREMIUM: Custom, full team
premium_tier = {
    "model": "PREMIUM",
    "total_range": {
        "min": INPUT["costs"]["total_range"]["max"] * 1.2,      # 120% of baseline
        "max": INPUT["costs"]["total_range"]["max"] * 1.8       # 180% of baseline
    },
    "philosophy": "Quality + team, higher burn",
    "team_size": 2-3,
    "timeline": "8 months"
}
```

**Step 2: Select Suppliers**

```python
# Based on business_type + location + selected tier
suppliers = {
    "Engineering": [
        {
            "name": "Upwork",
            "why_recommended": "Find backend engineers for $30-50/hr (LEAN/MID)",
            "url": "https://upwork.com",
            "cost": "Freelancer rates"
        },
        {
            "name": "Y Combinator Startup School",
            "why_recommended": "Startup advice + go-to-market mentorship",
            "url": "https://startupschool.org",
            "cost": "Free"
        }
    ],
    "Marketing": [
        {
            "name": "Google Local Services Ads",
            "why_recommended": "Best for local plumber/HVAC in SF ($X/day)",
            "url": "https://ads.google.com/lsa",
            "cost": "Pay-per-lead"
        }
    ]
}
```

**Step 3: Determine Team Needs**

```python
# Derive from ROOT CAUSES difficulty
team_needs = []

for cause in INPUT["root_causes"]:
    if cause["difficulty"] == "easy":
        # Can use freelancers, hire later
        team_needs.append({
            "title": "Backend Engineer",
            "type": "contract",
            "salary_range": {"min": 0, "max": 50},  # $/hour for contract
            "priority": "MUST_HAVE",
            "month": 1
        })
    elif cause["difficulty"] == "medium":
        # Need experienced person
        team_needs.append({
            "title": "Operations Manager",
            "type": "FTE",
            "salary_range": {"min": 60000, "max": 80000},
            "priority": "NICE_TO_HAVE",
            "month": 4  # After MVP
        })
    elif cause["difficulty"] == "hard":
        # Need specialized expertise
        team_needs.append({
            "title": "Supply Chain Manager",
            "type": "FTE",
            "salary_range": {"min": 80000, "max": 120000},
            "priority": "MUST_HAVE",
            "month": 6  # Before scale
        })
```

**Step 4: Create Timeline**

```python
# 12-month roadmap based on cost tier + complexity
timeline = {
    "VALIDATION": {
        "weeks": "4-6",
        "cost": tier["total_range"]["min"] * 0.15,  # 15% of budget
        "milestones": [
            "Landing page live",
            "100 waitlist signups",
            "5 user interviews completed",
            "Legal entity formed"
        ]
    },
    "BUILD MVP": {
        "weeks": "8-12",
        "cost": tier["total_range"]["min"] * 0.50,  # 50% of budget
        "milestones": [
            "Core product complete",
            "10 beta users",
            "Payment processing working",
            "Iteration based on feedback"
        ]
    },
    "LAUNCH": {
        "weeks": "2-4",
        "cost": tier["total_range"]["min"] * 0.20,  # 20% of budget
        "milestones": [
            "Public launch",
            "First 50 customers",
            "First employee hired",
            "Marketing campaign live"
        ]
    },
    "SCALE": {
        "weeks": "16-20",
        "cost": tier["total_range"]["min"] * 0.15,  # 15% of budget
        "milestones": [
            "$X monthly recurring revenue",
            "200+ customers",
            "Expand to 2nd market",
            "Team of 3"
        ]
    }
}
```

---

## User Experience Flow

### 1. After ANALYZE Complete

User clicks "SETUP" tab:

```
┌─ DECOMPOSE (✓ Done)
├─ DISCOVER (✓ Done)
├─ ANALYZE (✓ Done)
│  ├─ OPPORTUNITY
│  ├─ CUSTOMERS
│  ├─ COMPETITORS
│  ├─ ROOT CAUSES
│  └─ COSTS
└─ SETUP (← User here)
```

### 2. Load SETUP

Backend generates SetupResponse:

```python
@app.post("/api/analyze", response_model=SetupResponse)
async def setup_section(req: SetupRequest) -> SetupResponse:
    """Generate launch plan from ANALYZE data"""

    # User has selected cost tier (LEAN/MID/PREMIUM)
    tier = req.selected_tier  # "LEAN" | "MID" | "PREMIUM"

    # Generate based on prior ANALYZE results + selected tier
    cost_tiers = generate_cost_tiers(req.analysis_context)
    suppliers = select_suppliers(req.decomposition, req.analysis_context, tier)
    team = derive_team_needs(req.analysis_context["root_causes"], tier)
    timeline = create_timeline(req.analysis_context, tier)

    return SetupResponse(
        cost_tiers=cost_tiers,
        suppliers=suppliers,
        team=team,
        timeline=timeline
    )
```

### 3. Save to Idea

```
[Save Setup Plan] button
    ↓
PATCH /api/ideas/{idea_id}
    ↓
{
    "setup": SetupResponse,
    "status": "setup_completed"
}
    ↓
Saved to database
```

### 4. View Later (Dashboard)

User logs in → Dashboard → Click idea:

```
Dashboard:
  [Idea: Cold-pressed juice SF]
  ├─ Status: SETUP_COMPLETED ✓
  ├─ Modules: D✓ D✓ A✓ S✓ V✗
  └─ [View Full Analysis]

Idea Detail:
  Tabs: Overview | Discover | Analyze | Setup | Validate | Notes
         ────────────────────────────────────────────────────────
                                          (← Setup tab shows above plan)
```

---

## What Currently Exists vs What's Missing

| Component | Status | Details |
|-----------|--------|---------|
| **Schema** | ✅ Defined | SetupResponse + all sub-models exist |
| **Database** | ✅ Structured | setup field in ideas table |
| **API endpoint** | ❌ Missing | No POST /api/setup |
| **Logic** | ❌ Missing | No function to generate SetupResponse |
| **Prompts** | ❌ Missing | No LLM prompts for setup |
| **Frontend** | ❌ Missing | No Setup tab UI |
| **Saving** | ⚠️ Partial | Ideas.update() supports it, but no UI |
| **Login** | ✅ Done | Auth already exists |
| **Dashboard** | ⚠️ Partial | List ideas works, detail page TODO |

---

## Minimal Implementation (User POV)

To get SETUP working:

1. **Create `/api/setup` endpoint** (Generate SetupResponse from ANALYZE data)
2. **Create setup logic** (Convert ROOT CAUSES + COSTS → cost tiers + suppliers + team + timeline)
3. **Frontend: SETUP tab UI** (Show 4 sections: Cost Tiers, Suppliers, Team, Timeline)
4. **Add save button** (PATCH /api/ideas/{id} with setup data)
5. **Link to Dashboard** (Show setup status on idea cards)

All pieces to save/retrieve exist. Just need to generate + display.

