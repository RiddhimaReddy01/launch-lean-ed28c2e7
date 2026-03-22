# LaunchLens: Complete User Flow & System Architecture

## 🔄 Complete User Journey

```
┌──────────────────────────────────────────────────────────────────┐
│                   LAUNCHLENS USER JOURNEY                        │
└──────────────────────────────────────────────────────────────────┘

STEP 1: DISCOVERY
─────────────────
     User visits launchlens.com
            ↓
     [Landing Page] (/landing)
     "Start Analyzing Ideas"
            ↓
     Clicks "Start"
            ↓
     [Research Page] (/research)


STEP 2: ENTER IDEA
──────────────────
     User enters: "AI video editor for creators"
            ↓
     System triggers parallel fetch (useResearchParallel)
            ↓
     Shows loading spinner
            ↓
     [Loading Spinner]
     "Fetching all research modules..."


STEP 3: RESEARCH (5 MODULES RUNNING IN PARALLEL)
────────────────────────────────────────────────
     ┌─────────────┬──────────────┬────────────┬──────────┬───────────┐
     │  Module 1   │  Module 2    │ Module 3   │ Module 4 │ Module 5  │
     │  Decompose  │  Discover    │  Analyze   │  Setup   │ Validate  │
     │  (1-2s)     │  (2-3s)      │  (2-3s)    │  (2-3s)  │  (2-3s)   │
     ├─────────────┼──────────────┼────────────┼──────────┼───────────┤
     │ Business    │ Community    │ Market     │ Launch   │ Testing   │
     │ Breakdown   │ Signals      │ Analysis   │ Plan     │ Toolkit   │
     └─────────────┴──────────────┴────────────┴──────────┴───────────┘
            ↓              ↓              ↓            ↓           ↓
         All 5 run in PARALLEL (Promise.all)
            ├─ Takes ~3s instead of ~13s (4.3x faster!)
            └─ Results stored in IdeaContext


STEP 4: RESULTS DISPLAYED IN STEPPER
──────────────────────────────────────
     [Stepper Navigation]
     ● Discover   ● Analyze    ● Setup    ● Validate

     Tab 1: DISCOVER
     ├─ 234 community signals
     ├─ From 45 sources (Reddit, Google)
     ├─ Segmented by: Pain points, Discussions, Trends
     └─ Filter by source

     Tab 2: ANALYZE
     ├─ Market Size: $480M
     ├─ Competitors: 12 found (Capcut, Adobe Premiere, etc)
     ├─ Unfilled Gaps: Auto-captions, Trend detection
     ├─ Customer Segments: TikTok creators, YouTubers, Small agencies
     └─ Segment Deep-dive: Primary need, Size, Growth

     Tab 3: SETUP
     ├─ Cost Tiers: Indie ($50-100K), Standard ($100-150K), Enterprise
     ├─ Timeline: 16-24 weeks
     ├─ Team Composition: 1 engineer, 1 designer, 1 PM
     └─ Milestones: MVP (4 weeks), Beta (8 weeks), Launch (12 weeks)

     Tab 4: VALIDATE
     ├─ Landing Page Copy
     │  ├─ Headline: "AI video editing for creators"
     │  ├─ Benefits: Auto-cut, Captions, Trending effects
     │  └─ CTA: "Join the waitlist"
     ├─ Survey Questions (7 questions)
     │  ├─ How much time editing?
     │  ├─ Would you switch from Adobe?
     │  └─ Max price per month?
     ├─ WhatsApp Message
     │  └─ "Hey, we're building... [SURVEY_LINK]"
     ├─ Communities to Join (8 communities)
     │  ├─ r/TikTokCreators (45K members)
     │  ├─ r/VideoEditing (32K members)
     │  └─ Facebook: Content Creator Pro (120K members)
     └─ Validation Scorecard
        ├─ Waitlist Target: 150
        ├─ Survey Target: 50
        ├─ Switch Rate Target: 60%
        └─ Price Tolerance: $49-99/month


STEP 5: USER SAVES RESULTS
────────────────────────────
     User clicks [Save Results]
            ↓
     Check: Is user logged in?
            ├─ NO: Show SaveAuthModal
            │   ├─ Email: [__________]
            │   ├─ Password: [__________]
            │   └─ [Create Account]
            │       ↓
            │       POST /auth/v1/signup (Supabase)
            │       ├─ Create user record
            │       ├─ Hash password (bcrypt)
            │       └─ Return JWT token
            │           ↓
            │           localStorage.setItem('auth_token', jwt)
            │           ↓
            │           Auto-save idea
            │
            └─ YES: Direct save
                 ↓
                 POST /api/ideas
                 {
                   "title": "AI Video Editor",
                   "decomposition": {...},
                   "discover": {...},
                   "analyze": {...},
                   "setup": {...},
                   "validate": {...}
                 }
                 ↓
                 Backend receives JWT token from Authorization header
                 ↓
                 jwt.decode(token) → Extract user_id
                 ↓
                 INSERT INTO ideas (user_id, title, decomposition, ...)
                 ↓
                 Return idea_id: "550e8400-..."


STEP 6: IDEA SAVED TO DATABASE
─────────────────────────────────
     Database: Supabase PostgreSQL

     ideas table:
     ┌──────────┬──────────┬────────────┬──────────────────┐
     │    ID    │ USER_ID  │   TITLE    │  DECOMPOSITION   │
     ├──────────┼──────────┼────────────┼──────────────────┤
     │550e8400  │user-123  │AI Video... │{business_type...}
     │550e8401  │user-123  │AI Music... │{business_type...}
     └──────────┴──────────┴────────────┴──────────────────┘

     Fields stored:
     - decomposition (Module 1 output)
     - discover (Module 2 output)
     - analyze (Module 3 output)
     - setup (Module 4 output)
     - validate (Module 5 output)
     - tags (user-added: ["ai", "video", "saas"])
     - notes (user notes)
     - status (draft, archived, etc)


STEP 7: USER RUNS VALIDATION EXPERIMENTS
──────────────────────────────────────────
     User launches idea from saved research
            ↓
     Posts landing page in communities
     (r/TikTokCreators, r/VideoEditing, etc)
            ↓
     Collects metrics:
     - 187 waitlist signups
     - 42 survey completions
     - 65% would switch from Adobe
     - $75 average price tolerance
            ↓
     POST /api/validation-experiments
     {
       "idea_id": "550e8400-...",
       "metrics": {
         "waitlist_signups": 187,
         "would_switch_rate": 65,
         "price_tolerance_avg": 75
       }
     }
            ↓
     Backend calculates VERDICT:
     ├─ Signups: 187 (✓ > 150 target)
     ├─ Switch Rate: 65% (✓ > 60% target)
     ├─ Price Tolerance: $75 (✓ > $8 minimum)
     └─ RESULT: "GO" ✓
               "Strong demand signal with healthy price tolerance.
                Move forward with confidence."
            ↓
     User sees:
     [Verdict: GO] ✓
     "Strong demand signal..."

     Can also see: PIVOT (mixed signals) or KILL (low interest)


STEP 8: USER ACCOUNT (CURRENTLY MISSING)
──────────────────────────────────────────
     ❌ NO DASHBOARD YET

     What SHOULD exist (/dashboard):
     ├─ [Saved Ideas List]
     │  ├─ AI Video Editor    (Draft, 2026-03-21, All modules done)
     │  ├─ AI Music Generator (Draft, 2026-03-19, 3 modules done)
     │  └─ [+ New Analysis]
     │
     ├─ [Idea Detail] (/dashboard/ideas/550e8400-...)
     │  ├─ Title, Description, Tags
     │  ├─ Research Data (view all modules)
     │  ├─ Edit Notes
     │  ├─ Export to PDF
     │  └─ Validation Experiments
     │      ├─ Past experiments with verdicts
     │      └─ [+ New Experiment]
     │
     └─ [Profile]
        ├─ User email
        ├─ Password settings
        └─ Logout

     Currently only accessible via API:
     ├─ GET /api/ideas (list all)
     ├─ GET /api/ideas/{id} (view one)
     ├─ PATCH /api/ideas/{id} (edit)
     └─ DELETE /api/ideas/{id} (delete)
```

---

## 🏗️ System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React/Vite)                   │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  [Landing Page]      [Auth Page]      [Research Page]         │
│   (/landing)         (/auth)          (/research)             │
│   - Marketing        - Sign up        - Idea input            │
│   - CTA              - Login          - Stepper nav           │
│                      - JWT token      - Module display        │
│                                       - Save button           │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              Hooks & Context                            │ │
│  ├──────────────────────────────────────────────────────────┤ │
│  │ useResearchParallel()                                   │ │
│  │  ├─ Decompose first (dependency)                        │ │
│  │  └─ Then Promise.all([discover, analyze, setup, validate│ │
│  │                                                        │ │
│  │ IdeaContext                                             │ │
│  │  ├─ idea (string)                                       │ │
│  │  ├─ currentStep (discover|analyze|setup|validate)      │ │
│  │  ├─ storeAnalysis(section, data)                        │ │
│  │  └─ storeSetup(data)                                    │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              API Client (@/api/)                        │ │
│  ├──────────────────────────────────────────────────────────┤ │
│  │ decomposeIdea()                                          │ │
│  │ discoverInsights()                                       │ │
│  │ analyzeSection()                                         │ │
│  │ generateSetup()                                          │ │
│  │ generateValidation()                                     │ │
│  │ saveIdea()              ← POST /api/ideas               │ │
│  │ listIdeas()             ← GET /api/ideas                │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  LocalStorage:                                                 │
│  ├─ auth_token (JWT)                                          │
│  └─ user_email                                                │
│                                                                │
└────────────────────────────────────────────────────────────────┘
                             ↕ HTTPS ↕
              (All requests include JWT in Authorization header)
                             ↓
┌────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI/Python)                   │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Auth Layer (app/core/auth.py)                                │
│  ├─ require_user (raises 401 if no token)                    │
│  ├─ optional_user (returns None if no token)                 │
│  └─ JWT decode & verify                                       │
│                                                                │
│  API Endpoints:                                                │
│  ├─ POST /api/decompose-idea        → decompose.py           │
│  ├─ POST /api/discover-insights     → discover.py            │
│  ├─ POST /api/analyze-section       → analyze.py             │
│  ├─ POST /api/generate-setup        → setup.py               │
│  ├─ POST /api/generate-validation   → validate.py            │
│  ├─ POST /api/ideas                 → ideas.py               │
│  ├─ GET /api/ideas                  → ideas.py               │
│  ├─ GET /api/ideas/{id}             → ideas.py               │
│  ├─ PATCH /api/ideas/{id}           → ideas.py               │
│  ├─ DELETE /api/ideas/{id}          → ideas.py               │
│  ├─ POST /api/validation-experiments → tracking.py           │
│  └─ GET /api/validation-experiments/{id} → tracking.py       │
│                                                                │
│  Services:                                                     │
│  ├─ llm_client.py (Groq → Gemini → Fallback)                │
│  ├─ google_search.py (Serper API)                            │
│  ├─ reddit_scraper.py (PRAW library)                         │
│  ├─ data_cleaner.py (Deduplication & filtering)              │
│  └─ pdf_generator.py (Export to PDF)                         │
│                                                                │
│  Prompts:                                                      │
│  ├─ decompose_system / decompose_user                         │
│  ├─ discover_system / discover_user                           │
│  └─ validate_system / validate_user                           │
│                                                                │
│  Authentication:                                               │
│  ├─ Supabase Auth (manages users)                            │
│  └─ JWT tokens (verify requests)                             │
│                                                                │
└────────────────────────────────────────────────────────────────┘
                             ↕
                        DATABASES
                             ↓
┌────────────────────────────────────────────────────────────────┐
│              SUPABASE (PostgreSQL + Auth)                      │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  auth.users (managed by Supabase Auth)                        │
│  ├─ id (UUID)                                                 │
│  ├─ email                                                     │
│  ├─ password_hash (bcrypt)                                    │
│  ├─ created_at                                                │
│  └─ last_sign_in_at                                           │
│                                                                │
│  ideas (custom table)                                         │
│  ├─ id (UUID)                                                 │
│  ├─ user_id (FK → auth.users)                                │
│  ├─ title                                                     │
│  ├─ description                                               │
│  ├─ status (draft, archived)                                  │
│  ├─ decomposition (JSONB - Module 1)                          │
│  ├─ discover (JSONB - Module 2)                               │
│  ├─ analyze (JSONB - Module 3)                                │
│  ├─ setup (JSONB - Module 4)                                  │
│  ├─ validate (JSONB - Module 5)                               │
│  ├─ tags                                                      │
│  ├─ notes                                                     │
│  ├─ created_at                                                │
│  └─ updated_at                                                │
│                                                                │
│  validation_experiments (custom table)                        │
│  ├─ id (UUID)                                                 │
│  ├─ user_id (FK → auth.users)                                │
│  ├─ idea_id (FK → ideas)                                      │
│  ├─ methods (landing_page, survey, community, etc)            │
│  ├─ waitlist_signups                                          │
│  ├─ survey_completions                                        │
│  ├─ would_switch_rate                                         │
│  ├─ price_tolerance_avg                                       │
│  ├─ verdict (go, pivot, kill, awaiting)                       │
│  ├─ reasoning                                                 │
│  ├─ created_at                                                │
│  └─ updated_at                                                │
│                                                                │
└────────────────────────────────────────────────────────────────┘
                             ↕
                      EXTERNAL APIs
                             ↓
┌────────────────────────────────────────────────────────────────┐
│                    LLM Providers                               │
├────────────────────────────────────────────────────────────────┤
│ Groq (Primary) → Gemini (Fallback) → Deterministic (Always)   │
│ Model: openai/gpt-oss-20b                                      │
│ Backup: gemini-pro                                             │
│ Always: Pre-written fallback for each module                  │
└────────────────────────────────────────────────────────────────┘
                             +
┌────────────────────────────────────────────────────────────────┐
│                    Data Sources                                │
├────────────────────────────────────────────────────────────────┤
│ Serper (Google Search) + Reddit API (PRAW)                    │
│ ├─ Community discovery queries                                │
│ ├─ Market research queries                                    │
│ ├─ Competitor research                                        │
│ └─ Trend analysis                                             │
└────────────────────────────────────────────────────────────────┘
```

---

## ⏱️ Performance Timeline

```
User enters idea "AI Video Editor"
         ↓
    T+0s START
         ↓
    T+1s ✓ Decompose complete (business structure)
         ├─ Results: business_type, location, target_customers, price_tier
         ↓
    T+1.5s ✓ Discover starts in parallel (with others)
    T+1.5s ✓ Analyze starts in parallel
    T+1.5s ✓ Setup starts in parallel
    T+1.5s ✓ Validate starts in parallel
         ├─ All 4 running simultaneously via Promise.all()
         ↓
    T+3.5s ✓ All 4 complete (assuming ~2 second each)
    T+3.5s TOTAL TIME: 3.5 seconds
         ↓
    Results displayed in UI stepper
    User can navigate between tabs
         ↓
    T+35s User clicks "Save Results"
         ↓
    POST /api/ideas sent to backend
         ↓
    Backend saves to database
    Returns: {"id": "550e8400...", "status": "draft"}
         ↓
    ✓ COMPLETE

PERFORMANCE METRICS:
─────────────────────
Before optimization: 13 seconds (sequential)
After optimization: ~3-5 seconds (parallel + preprocessing)
Improvement: 2.6x - 4.3x faster

Achievable with further optimization:
- Caching: 2-3 seconds
- Backend parallelization: 1-2 seconds
```

---

## 🔐 Security Flow

```
User Signup Flow:
─────────────────
1. User enters email & password on /auth
2. Frontend calls: POST supabase.auth.signUp({email, password})
3. Supabase:
   ├─ Validates email format
   ├─ Hashes password with bcrypt
   ├─ Creates user record in auth.users
   └─ Returns: {access_token, user}
4. Frontend:
   ├─ localStorage.setItem('auth_token', access_token)
   └─ Redirects to /research

API Request with Authentication:
─────────────────────────────────
1. Frontend makes request:
   POST /api/ideas
   Headers: {
     'Authorization': 'Bearer {jwt_token}',
     'Content-Type': 'application/json'
   }
2. Backend:
   ├─ Extracts token from Authorization header
   ├─ Verifies signature with Supabase public key
   ├─ Decodes token → {sub: user_id, email, exp, iat}
   ├─ Checks expiration (exp > current_time)
   └─ Returns user_id to handler
3. Handler:
   ├─ Receives user_id from Depends(require_user)
   ├─ Inserts idea with user_id
   └─ Only returns ideas where user_id matches

Token Expiration:
─────────────────
1. Token expires after 1 hour (Supabase default)
2. Invalid/expired token → 401 Unauthorized
3. Frontend should:
   ├─ Clear localStorage
   ├─ Redirect to /auth
   └─ User logs in again to get new token
```

