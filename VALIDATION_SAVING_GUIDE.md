# Validation Module, Saving, Tracking & User Account

## 🎯 The Validation Module (Module 5)

### What It Does
The Validation Module generates a **complete toolkit to test if customers actually want your product**.

**Input**:
- Business decomposition (from Module 1)
- Customer insight (from Module 2)
- Market analysis (from Module 2)
- Launch plan costs & timeline (from Module 3)

**Output**: Five validation artifacts

### The 5 Validation Artifacts

#### 1. **Landing Page Copy**
Generated based on customer pain points and market positioning.

```json
{
  "headline": "AI-powered video editing for TikTok creators",
  "subheadline": "Create viral videos in minutes, not hours",
  "benefits": [
    "Auto-cut long videos into viral shorts",
    "AI-powered captions that match trends",
    "One-click trending effects"
  ],
  "cta_text": "Join the waitlist",
  "social_proof_quote": "This saved me 10 hours per week - @CreatorName"
}
```

**Why**: Test if your value proposition resonates with real customers via a landing page. Measure: Waitlist signups.

#### 2. **Survey Questions**
Up to 7 questions tailored to validate specific assumptions.

```json
{
  "title": "Quick Survey - Help us improve",
  "questions": [
    {
      "question": "How much time do you currently spend editing videos?",
      "type": "multiple_choice",
      "options": ["<1 hour/week", "1-5 hours/week", "5-10 hours/week", ">10 hours/week"]
    },
    {
      "question": "Would you switch from Adobe Premiere to save 5+ hours per week?",
      "type": "yes_no"
    },
    {
      "question": "What's the max you'd pay per month?",
      "type": "open_text"
    }
  ]
}
```

**Why**: Measure willingness-to-switch (switching intent) and price tolerance directly from users. Measure: Survey completions, switch rate, average price tolerance.

#### 3. **WhatsApp Message**
A templated message to engage users in relevant communities.

```json
{
  "message": "Hey! We're building an AI video editor for creators. It auto-cuts long videos into viral shorts and adds trending effects. Want to try it for free? [SURVEY_LINK] - No spam, promise!",
  "tone_note": "Casual, friendly, value-first (no hard sell)"
}
```

**Why**: Reach users where they already hang out. Better conversion than cold outreach.

#### 4. **Communities List**
Pre-researched communities where target customers gather.

```json
{
  "communities": [
    {
      "name": "TikTok Creators",
      "platform": "reddit",
      "member_count": 45000,
      "rationale": "Highly engaged community of short-form video creators",
      "link": "https://reddit.com/r/TikTokCreators"
    },
    {
      "name": "Content Creator Pro",
      "platform": "facebook",
      "member_count": 120000,
      "rationale": "Diverse creator community with active moderation",
      "link": "https://facebook.com/groups/ContentCreatorPro"
    }
  ]
}
```

**Why**: No cold outreach. Join existing communities of your target customers.

#### 5. **Validation Scorecard**
Clear targets to validate before moving forward.

```json
{
  "scorecard": {
    "waitlist_target": 150,
    "survey_target": 50,
    "switch_pct_target": 60,
    "price_tolerance_target": "$49-99/month"
  }
}
```

---

## 💾 How Users Save Analysis

### The Complete Flow

#### Step 1: User Analyzes Idea
```
User enters: "AI-powered video editor"
↓
System runs 5 modules in parallel (decompose, discover, analyze, setup, validate)
↓
Results show in UI (decomposition, insights, analysis, setup plan, validation toolkit)
```

#### Step 2: User Clicks "Save Results"

**Without Account**:
- SaveAuthModal pops up inline
- User creates account (email + password)
- Supabase generates JWT token
- Token stored in localStorage
- Idea auto-saves to database

**With Account**:
- Direct save (already authenticated)

#### Step 3: Idea Saved to Database

**Database Schema** (ideas table):
```sql
CREATE TABLE ideas (
  id UUID PRIMARY KEY,
  user_id UUID (from JWT),
  title TEXT,
  description TEXT,
  status TEXT ('draft', 'archived', etc),
  decomposition JSONB,      -- Module 1 output
  discover JSONB,            -- Module 2 output
  analyze JSONB,             -- Module 3 output
  setup JSONB,               -- Module 4 output
  validate JSONB,            -- Module 5 output
  tags TEXT[],               -- User-added tags
  notes TEXT,                -- User notes
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

### What Gets Saved

The SaveIdeaRequest includes:

```typescript
{
  title: "AI Video Editor",                // User-provided
  description: "A tool for creators...",   // Optional
  decomposition: { ... },                  // Module 1
  discover: { ... },                       // Module 2
  analyze: { ... },                        // Module 3
  setup: { ... },                          // Module 4
  validate: { ... },                       // Module 5
  tags: ["ai", "video", "saas"],          // Optional
  notes: "Follow up with these communities..." // Optional
}
```

### API Endpoints for Saving

#### POST /api/ideas
Save a new idea with all research data.

```bash
curl -X POST http://localhost:8001/api/ideas \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "AI Video Editor",
    "decomposition": { ... },
    "discover": { ... },
    "analyze": { ... },
    "setup": { ... },
    "validate": { ... }
  }'
```

**Response**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "AI Video Editor",
  "status": "draft",
  "created_at": "2026-03-21T10:30:00Z",
  "has_decompose": true,
  "has_discover": true,
  "has_analyze": true,
  "has_setup": true,
  "has_validate": true,
  "tags": []
}
```

#### GET /api/ideas
List all saved ideas for authenticated user.

```bash
curl http://localhost:8001/api/ideas \
  -H "Authorization: Bearer {jwt_token}"
```

**Response**:
```json
[
  {
    "id": "550e8400...",
    "title": "AI Video Editor",
    "status": "draft",
    "created_at": "2026-03-21T10:30:00Z",
    "has_decompose": true,
    "has_discover": true,
    "has_analyze": true,
    "has_setup": true,
    "has_validate": true
  },
  {
    "id": "550e8401...",
    "title": "AI Music Generator",
    "status": "draft",
    "created_at": "2026-03-19T14:22:00Z",
    "has_decompose": true,
    "has_discover": true,
    ...
  }
]
```

#### GET /api/ideas/{idea_id}
Retrieve full idea with all research data.

```bash
curl http://localhost:8001/api/ideas/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer {jwt_token}"
```

**Response**: Complete idea with all modules' data.

#### PATCH /api/ideas/{idea_id}
Update specific sections of an idea.

```bash
curl -X PATCH http://localhost:8001/api/ideas/550e8400... \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "notes": "Updated: Follow up with r/TikTokCreators",
    "tags": ["ai", "video", "saas", "follow-up"]
  }'
```

#### DELETE /api/ideas/{idea_id}
Delete an idea.

```bash
curl -X DELETE http://localhost:8001/api/ideas/550e8400... \
  -H "Authorization: Bearer {jwt_token}"
```

---

## 📊 Tracking System (Validation Experiments)

### What Is Tracking?

Users can log the **actual results** of running their validation experiments and get a GO/PIVOT/KILL verdict.

### How It Works

#### Step 1: User Runs Validation Experiments
- Launches landing page in communities
- Posts WhatsApp message to groups
- Collects survey responses
- Measures results

#### Step 2: User Enters Metrics

**Metrics to Track**:
```json
{
  "idea_id": "550e8400-e29b-41d4-a716-446655440000",
  "methods": ["landing_page", "survey", "community_engagement"],
  "metrics": {
    "waitlist_signups": 187,
    "survey_completions": 42,
    "would_switch_rate": 65,
    "price_tolerance_avg": 75,
    "community_engagement": 234,
    "reddit_upvotes": 89
  }
}
```

#### Step 3: System Generates Verdict

The tracking system analyzes metrics using decision rules:

**GO** (Strong signal):
- Waitlist signups ≥ 150 AND
- Switch rate ≥ 60% AND
- Price tolerance ≥ $8/month
- → "Strong demand signal. Move forward with confidence."

**PIVOT** (Mixed signals):
- Waitlist signups 80-149 OR
- Switch rate 40-59% OR
- Price tolerance < $6 but signups > 50
- → "Moderate interest — refine positioning, pricing, or segment."

**KILL** (Low signal):
- Waitlist signups < 30 AND
- Switch rate < 30%
- → "Low interest. Consider fundamentally different value prop."

**AWAITING** (No data):
- No metrics entered yet
- → "Enter your experiment results to get a recommendation."

### API Endpoints for Tracking

#### POST /api/validation-experiments
Save validation experiment results.

```bash
curl -X POST http://localhost:8001/api/validation-experiments \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "idea_id": "550e8400-e29b-41d4-a716-446655440000",
    "methods": ["landing_page", "survey"],
    "metrics": {
      "waitlist_signups": 187,
      "survey_completions": 42,
      "would_switch_rate": 65,
      "price_tolerance_avg": 75,
      "community_engagement": 234,
      "reddit_upvotes": 89
    }
  }'
```

**Response**:
```json
{
  "id": "exp-123456",
  "idea_id": "550e8400...",
  "methods": ["landing_page", "survey"],
  "waitlist_signups": 187,
  "survey_completions": 42,
  "would_switch_rate": 65,
  "price_tolerance_avg": 75,
  "verdict": "go",
  "reasoning": "Strong demand signal with healthy price tolerance. Move forward with confidence.",
  "created_at": "2026-03-21T15:45:00Z"
}
```

#### GET /api/validation-experiments/{idea_id}
Fetch all validation experiments for an idea.

```bash
curl http://localhost:8001/api/validation-experiments/550e8400... \
  -H "Authorization: Bearer {jwt_token}"
```

#### PATCH /api/validation-experiments/{id}
Update experiment metrics.

```bash
curl -X PATCH http://localhost:8001/api/validation-experiments/exp-123456 \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "metrics": {
      "waitlist_signups": 200
    }
  }'
```

---

## 👤 User Account (What They See)

### Current State (Frontend Pages)

#### 1. **Landing Page** (`/`)
- Marketing page
- Call-to-action: "Start Analyzing"

#### 2. **Auth Page** (`/auth`)
- Sign up / Login form
- Email + password
- Creates JWT token
- Redirects to Research

#### 3. **Research Page** (`/research`)
- Main analysis interface
- 4 step stepper: Discover → Analyze → Setup → Validate
- Shows loading state while fetching modules in parallel
- Displays:
  - Module 1: Community signals (Reddit, Google)
  - Module 2: Market opportunity (SOM, competitors, customer segments)
  - Module 3: Launch plan (costs, timeline, team)
  - Module 4: Validation toolkit (landing page, survey, communities, scorecard)
- **Save Results** button
  - If not logged in: Opens SaveAuthModal (inline signup)
  - If logged in: Saves directly to database

### Missing: Dashboard / Saved Ideas

**Currently NOT built**:
- ❌ Dashboard showing all saved ideas
- ❌ View saved idea details
- ❌ Edit notes/tags on saved idea
- ❌ Validation experiment tracking UI
- ❌ History of all analyses

**What should be there** (if built):
```
/dashboard
├── Saved Ideas List
│   ├── Title, status, created date
│   ├── Progress (which modules completed)
│   ├── Last updated
│   └── Actions (view, edit, delete, run validation)
├── Idea Detail View (/dashboard/ideas/{id})
│   ├── Full research analysis
│   ├── Edit notes/tags
│   ├── Export to PDF
│   └── Validation Experiments section
│       ├── List past experiments
│       ├── Add new experiment
│       └── View verdicts (GO/PIVOT/KILL)
└── Profile
    ├── User settings
    ├── Account info
    └── Logout
```

---

## 🔄 Complete User Flow

### Scenario: User Analyzes "AI Video Editor"

```
1. User visits /
   └─ Sees landing page
   └─ Clicks "Start Analyzing"

2. Redirects to /research
   └─ Prompted to enter idea
   └─ Enters: "AI-powered video editor for TikTok creators"

3. Backend runs 5 modules in parallel:
   ├─ Decompose: Business structure
   ├─ Discover: Reddit/Google signals
   ├─ Analyze: Market opportunity & competitors
   ├─ Setup: Launch plan with costs
   └─ Validate: Landing page copy, survey, communities

4. Frontend displays results in stepper:
   ├─ Discover tab: 234 community signals from 45 sources
   ├─ Analyze tab: $480M SOM, 12 competitors, 3 customer segments
   ├─ Setup tab: $50-150K launch cost, 16-week timeline
   └─ Validate tab: Landing page, survey, 8 communities, scorecard

5. User clicks "Save Results"
   ├─ If not logged in:
   │  ├─ SaveAuthModal appears
   │  ├─ User signs up (email: alice@example.com)
   │  ├─ JWT token generated
   │  └─ Token stored in localStorage
   └─ If logged in:
      └─ Direct save

6. POST /api/ideas sent to backend:
   └─ Saves all 5 modules + metadata
   └─ Returns idea ID: "550e8400-..."

7. User can now:
   ├─ Go back and analyze another idea
   ├─ (If dashboard existed):
   │  ├─ View all saved ideas
   │  ├─ Launch landing page from saved setup
   │  └─ Log validation experiment results
   └─ Get GO/PIVOT/KILL verdict
```

---

## 📱 Frontend Components (Current)

### Research.tsx
- Uses `useResearchParallel` hook
- Fetches all 5 modules in parallel
- Passes data to individual module components
- Shows loading spinner while fetching
- Renders stepper navigation

### Module Components
- `DiscoverModule.tsx` - Shows community signals
- `AnalyzeModule.tsx` - Shows market analysis
- `SetupModule.tsx` - Shows launch plan
- `ValidateModule.tsx` - Shows validation toolkit
- `SaveAuthModal.tsx` - Inline signup modal

---

## 🗄️ Database Schema

### ideas table
```
id          UUID (primary key)
user_id     UUID (foreign key → auth.users)
title       TEXT
description TEXT
status      TEXT (draft, archived, etc)
decomposition  JSONB
discover    JSONB
analyze     JSONB
setup       JSONB
validate    JSONB
tags        TEXT[]
notes       TEXT
created_at  TIMESTAMP
updated_at  TIMESTAMP
```

### validation_experiments table
```
id          UUID (primary key)
user_id     UUID (foreign key → auth.users)
idea_id     UUID (foreign key → ideas)
methods     TEXT[] (landing_page, survey, etc)
waitlist_signups         INTEGER
survey_completions       INTEGER
would_switch_rate        FLOAT (0-100)
price_tolerance_avg      FLOAT ($)
community_engagement     INTEGER
reddit_upvotes          INTEGER
verdict     TEXT (go, pivot, kill, awaiting)
reasoning   TEXT
created_at  TIMESTAMP
updated_at  TIMESTAMP
```

---

## 🚀 What's Missing (Next Steps)

1. **Dashboard Page** - List all saved ideas
2. **Idea Detail Page** - View full saved research + edit notes
3. **Validation Experiment UI** - Enter metrics, see verdicts
4. **PDF Export** - Download analysis as PDF
5. **Advanced Analysis** - Risks, pricing strategies, financials, customer acquisition
6. **Collaboration** - Share ideas with team members
7. **Templates** - Pre-built validation landing pages and surveys

---

## Summary

| Component | What It Does | Output |
|-----------|-------------|--------|
| **Validation Module** | Generates testing toolkit | Landing page copy, survey, communities, scorecard |
| **Save Endpoint** | Stores all research data | Idea ID, stored in database with user_id |
| **Ideas Endpoints** | Manage saved research | CRUD operations (create, read, update, delete) |
| **Tracking System** | Logs experiment results | GO/PIVOT/KILL verdict based on metrics |
| **User Account** | Shows what user owns | ❌ Missing: Dashboard (needs to be built) |

