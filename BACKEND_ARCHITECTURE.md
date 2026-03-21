# LaunchLens Backend Architecture Explained

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React/Vite)                     │
│              http://localhost:8085 (or 8084)                 │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP Requests
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI Backend                             │
│              http://localhost:8001                           │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                 API Router Layer                     │   │
│  │  (Defines HTTP endpoints: /api/decompose-idea, etc) │   │
│  └──────────────────────────────────────────────────────┘   │
│                         │                                    │
│  ┌──────────┬──────────┼──────────┬──────────┬────────────┐ │
│  ▼          ▼          ▼          ▼          ▼            ▼ │
│ decompose discover   analyze    setup    validate      stream│
│ (/api/)   (/api/)    (/api/)    (/api/)  (/api/)        │
│   │        │         │          │        │              │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                     │
│  ┌────────────────────▼─────────────────────────────────┐  │
│  │           Services Layer                            │  │
│  │  ┌─────────────────┬─────────────────────────────┐  │  │
│  │  │  LLM Client     │  Google Search (Serper)     │  │  │
│  │  │  ├─ Groq        │  ├─ Market research        │  │  │
│  │  │  ├─ Gemini      │  ├─ Competitor data        │  │  │
│  │  │  └─ Fallback    │  └─ Search results         │  │  │
│  │  │                 │                            │  │  │
│  │  │ Data Cleaner    │ Reddit Scraper             │  │  │
│  │  │ ├─ Parse JSON   │ ├─ Community posts         │  │  │
│  │  │ ├─ Normalize    │ └─ Discussion threads      │  │  │
│  │  │ └─ Validate     │                            │  │  │
│  │  │                 │ Preprocessor (NEW)         │  │  │
│  │  │                 │ ├─ Fetch parallel          │  │  │
│  │  │                 │ ├─ Deduplicate             │  │  │
│  │  │                 │ └─ Summarize               │  │  │
│  │  └─────────────────┴─────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────┘  │
│                       │                                     │
│  ┌────────────────────▼─────────────────────────────────┐  │
│  │         Database & External APIs                   │  │
│  │                                                    │  │
│  │  Supabase (PostgreSQL)  ◄── User data, Ideas    │  │
│  │  Groq API              ◄── LLM analysis          │  │
│  │  Google Gemini         ◄── Fallback LLM          │  │
│  │  Google Serper         ◄── Web search            │  │
│  │  Reddit API            ◄── Community insights    │  │
│  └────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Components Explained

### 1. API Router (`app/api/router.py`)
**What it does**: Central hub that connects all endpoints

```python
# Includes routers from all modules
router.include_router(decompose.router)
router.include_router(discover.router)
router.include_router(analyze.router)
router.include_router(setup.router)
router.include_router(validate.router)
router.include_router(research_stream.router)  # Streaming
```

**Why**: Keeps main.py clean, single place to add/remove endpoints

---

### 2. API Endpoints (5 Main Research Modules)

#### **Module 1: DECOMPOSE** (`app/api/decompose.py`)
**Input**: Raw business idea string
```json
{
  "idea": "AI-powered video editor for content creators"
}
```

**Process**:
1. Clean input (remove extra whitespace)
2. Validate (minimum 3 words)
3. Check cache (return if already analyzed)
4. Infer vertical (SaaS, food, local service, etc.)
5. Get domain defaults for that vertical
6. **Call LLM** with curated prompt
7. Post-process (normalize states, validate JSON)
8. Cache result (15 minutes)

**Output**: Structured decomposition
```json
{
  "business_type": "AI video editing software (SaaS)",
  "location": {
    "city": "San Francisco",
    "state": "CA"
  },
  "target_customers": ["Content creators", "Small agencies"],
  "price_tier": "premium ($49-$99/month)",
  "source_domains": ["producthunt.com", "g2.com", ...],
  "subreddits": ["videography", "smallbusiness"],
  "review_platforms": ["trustpilot", "g2"],
  "search_queries": ["AI video editor reviews", ...]
}
```

**Fallback**: If all LLMs fail, returns deterministic response (not fake data)

---

#### **Module 2: DISCOVER** (`app/api/discover.py`)
**Input**: Decomposition from Module 1

**Process**:
1. Run Serper search with queries from decomposition
2. Fetch 200+ web results, Reddit posts, review data
3. **Call LLM** to analyze and categorize insights
4. Extract pain points, unmet wants, market gaps, trends
5. Generate evidence with real quotes

**Output**: Market insights with sources
```json
{
  "insights": [
    {
      "type": "pain_point",
      "title": "Expensive video editing takes too long",
      "evidence": [
        {
          "quote": "Adobe Premiere is $55/month and slow",
          "source": "reddit:videography",
          "score": 142
        }
      ],
      "frequency": 95,
      "intensity_note": "People frustrated"
    }
  ]
}
```

**Key**: Uses real community data, not made up

---

#### **Module 3: ANALYZE** (`app/api/analyze.py`)
**Input**: Decomposition + selected insight

**Process**:
1. Determines analysis section (opportunity, competitors, risks, costs, timeline)
2. Fetches competitor data using Serper
3. **Calls LLM** 3x in parallel:
   - Opportunity analysis
   - Competitive landscape
   - Risk assessment
4. Combines results

**Output**: Detailed market analysis
```json
{
  "section": "opportunity",
  "data": {
    "tam": "Total addressable market: $10B/year",
    "competitors": ["Adobe", "CapCut", "DaVinci"],
    "opportunities": ["Ease of use gap", "Price gap"],
    "risks": ["Market dominance by Adobe"]
  }
}
```

**Note**: Runs 3 analyses in parallel (faster)

---

#### **Module 4: SETUP** (`app/api/setup.py`)
**Input**: Decomposition + analysis context

**Process**:
1. Creates cost structure (development, marketing, operations)
2. Searches for suppliers and team
3. **Calls LLM** to generate launch plan
4. Creates timeline and milestones

**Output**: Actionable launch plan
```json
{
  "costs": {
    "development": "$50-100K",
    "marketing": "$20-50K",
    "operations": "$5-10K/month"
  },
  "team_needed": ["3 engineers", "1 designer", "1 product manager"],
  "timeline": {
    "mvp": "3 months",
    "launch": "6 months",
    "profitability": "18-24 months"
  }
}
```

---

#### **Module 5: VALIDATE** (`app/api/validate.py`)
**Input**: Decomposition + all prior analysis

**Process**:
1. Identifies target customers
2. Searches for communities (Reddit, Discord, Twitter)
3. **Calls LLM** to generate validation strategy
4. Creates messaging and testing plan

**Output**: Validation communities & strategy
```json
{
  "communities": [
    {
      "platform": "reddit",
      "name": "videography",
      "strategy": "Post in feedback thread asking about pain points"
    }
  ],
  "landing_page_copy": "AI video editor that saves you hours...",
  "survey_questions": [...],
  "validation_timeline": "2-4 weeks"
}
```

---

### 3. Services Layer

#### **LLM Client** (`app/services/llm_client.py`)
Manages AI API calls with automatic fallback:

```
Priority Order:
1. Groq (fastest, free tier)
   - Model: openai/gpt-oss-20b
   - Speed: ~1-2 seconds
   - Cost: Free

2. Google Gemini (fallback)
   - Model: gemini-2.0-flash
   - Speed: ~2-3 seconds
   - Cost: Free tier (rate limited)

3. Fallback (deterministic)
   - No API call
   - Speed: Instant
   - Cost: Free
   - Quality: Basic but valid
```

**How it works**:
```python
# Sends same prompt to all providers until one succeeds
try:
    response = await call_groq(prompt)
except:
    try:
        response = await call_gemini(prompt)
    except:
        response = fallback_response()  # Always returns something
```

**Why**: Never crashes, always returns valid data

---

#### **Google Search** (`app/services/google_search.py`)
Fetches market data:

```python
run_search_queries(["AI video editor reviews", ...])
# Returns:
[
  {
    "title": "Best AI video editors 2026",
    "snippet": "Adobe Express, CapCut, DaVinci...",
    "url": "example.com",
    "score": 142
  },
  ...
]
```

---

#### **Data Cleaner** (`app/services/data_cleaner.py`)
Validates and normalizes LLM responses:

```python
clean_search_results(raw_data)
# Removes: Duplicates, invalid JSON, spam
# Normalizes: Dates, links, prices

normalize_state("california")  # → "CA"
```

---

#### **Preprocessor** (`app/services/preprocessor.py`) **NEW**
Curates data before LLM:

```python
curate_market_data(raw_data, limit=50)
# Sorts by relevance, removes duplicates, tops 50

summarize_posts(posts)
# Groups by: pain_points, features_wanted, pricing_concerns
```

---

### 4. Data Models (Schemas)

**Request Models** (`app/schemas/models.py`):
```python
class DecomposeRequest(BaseModel):
    idea: str

class AnalyzeRequest(BaseModel):
    decomposition: DecomposeResponse
    section: str
    insight: Optional[Any] = None
```

**Response Models**:
```python
class DecomposeResponse(BaseModel):
    business_type: str
    location: Location
    target_customers: List[str]
    price_tier: str
    source_domains: List[str]
    subreddits: List[str]
    review_platforms: List[str]
    search_queries: List[str]
```

---

### 5. Authentication & Database (`app/core/`)

#### **Auth** (`app/core/auth.py`)
```python
# JWT tokens from Supabase
optional_user = Depends(get_current_user)

# Routes can access: user email, ID, permissions
# Allows: Saving ideas to database with user ownership
```

#### **Config** (`app/core/config.py`)
```python
class Settings:
    GROQ_API_KEY = env("GROQ_API_KEY")
    GEMINI_API_KEY = env("GEMINI_API_KEY")
    SUPABASE_URL = env("SUPABASE_URL")
    SUPABASE_ANON_KEY = env("SUPABASE_ANON_KEY")
```

---

## Data Flow Example

### User enters: "AI-powered video editor"

```
┌─ Frontend ────────────────────────────────────────┐
│                                                    │
│  User types: "AI-powered video editor"            │
│                   │                                │
│                   ▼                                │
│           Click "Discover"                        │
│                   │                                │
└──────────────────┼────────────────────────────────┘
                   │ POST /api/decompose-idea
                   ▼
         ┌─ Backend ──────────────────────────┐
         │                                     │
         │  1. Validate (3+ words?) ✓         │
         │  2. Check cache → Miss             │
         │  3. Infer vertical → "saas_b2b"   │
         │  4. Get defaults → domains list   │
         │  5. Build prompt + system prompt  │
         │  6. Call Groq LLM [2s]            │
         │     Input: idea, vertical, domains │
         │     Output: JSON                   │
         │  7. Post-process → normalize      │
         │  8. Cache for 15 min              │
         │                                     │
         └─────────────┬──────────────────────┘
                       │ Returns DecomposeResponse
                       ▼
         ┌─ Frontend ──────────────────────────┐
         │                                     │
         │  Show "Discovering insights..."    │
         │  Call /api/discover-insights       │
         │           │                         │
         └───────────┼─────────────────────────┘
                     │
                     ▼
         ┌─ Backend ──────────────────────────┐
         │                                     │
         │  1. Get search queries from step 1 │
         │  2. Serper search × 8 queries      │
         │     → 200+ results                 │
         │  3. Fetch Reddit/Yelp data        │
         │  4. Call Gemini LLM [2s]          │
         │     Input: posts + analysis rules │
         │     Output: categorized insights  │
         │  5. Extract evidence quotes       │
         │                                     │
         └─────────────┬──────────────────────┘
                       │
                       ▼
         ┌─ Frontend ──────────────────────────┐
         │ Show: 8-15 insights with sources  │
         │ User can click to analyze further  │
         └─────────────────────────────────────┘
```

---

## Request/Response Cycle

### Typical Request
```
POST /api/decompose-idea
Content-Type: application/json

{
  "idea": "AI-powered video editor for content creators"
}
```

### Typical Response
```
HTTP/1.1 200 OK
Content-Type: application/json

{
  "business_type": "AI video editing software (SaaS)",
  "location": {"city": "San Francisco", "state": "CA", ...},
  "target_customers": ["Content creators", ...],
  "price_tier": "premium ($49-$99/month)",
  "source_domains": ["producthunt.com", "g2.com", ...],
  "subreddits": ["videography", "smallbusiness"],
  "review_platforms": ["trustpilot", "g2"],
  "search_queries": ["AI video editor reviews", ...]
}
```

---

## Error Handling

### Graceful Degradation
```
1. LLM Call Fails (403, timeout, etc)
   ↓
2. Try next provider (fallback chain)
   ↓
3. All fail?
   ↓
4. Return valid fallback response
   ↓
5. Never crash, always return something valid
```

### Example
```python
try:
    response = await call_groq(...)  # 403 Forbidden
except AllProvidersExhaustedError:
    # Return fallback decomposition (not mock)
    return _fallback_decompose(idea, vertical, defaults)
    # Returns: {"business_type": idea, "location": {}, ...}
```

---

## Performance Optimizations

### Caching
```python
# 15-minute cache per idea
_cache_store = {}
_cache_get(idea)  # Returns if not expired
_cache_set(idea, response)  # Stores with TTL
```

### Parallel Requests (NEW)
```python
# Run 3 analyses in parallel
results = await asyncio.gather(
    analyze_section('opportunity', ...),
    analyze_section('competitors', ...),
    analyze_section('risks', ...),
    return_exceptions=True
)
```

### Streaming Results (NEW)
```python
@app.get("/api/research-stream")
async def research_stream(idea: str):
    # Sends results as Server-Sent Events
    # Frontend gets updates in real-time
    yield format_sse("decompose", "complete", data, 20)
    yield format_sse("discover", "complete", data, 40)
    # ... etc
```

---

## Database Integration

### Supabase Tables
```sql
-- Users (authenticated via JWT)
-- Ideas (user's saved research)
-- Analyses (cached analysis results)
-- Progress (module completion status)
```

### Saving an Idea
```python
POST /api/ideas
{
  "title": "AI Video Editor",
  "decomposition": {...},
  "insights": {...}
}

# Saved to: ideas table (user_id indexed)
```

---

## Summary

| Component | Purpose | Speed | Failure |
|-----------|---------|-------|---------|
| **Decompose** | Extract structure | 2-5s | Falls back |
| **Discover** | Find market signals | 2-3s | Returns empty |
| **Analyze** | Generate insights | 2-3s | Partial data |
| **Setup** | Create plan | 2-3s | Generic plan |
| **Validate** | Find communities | 2-3s | Defaults |
| **LLM Chain** | Groq→Gemini→Fallback | 1-2s each | Always works |
| **Cache** | Reduce API calls | instant | 15 min TTL |
| **Stream** | Real-time progress | parallel | Progressive |

---

## Key Design Principles

1. **Never Crash**: Fallback for every failure
2. **Always Return Valid Data**: Even if partial
3. **Parallel When Possible**: Analyses run together
4. **Cache Aggressively**: 15 min for common ideas
5. **Stream Results**: Show progress, don't block
6. **Pre-process Data**: Give LLM only curated input
7. **Separate Concerns**: Each service has one job

