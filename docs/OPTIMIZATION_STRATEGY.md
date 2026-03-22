# LaunchLens Performance Optimization Strategy

## Current Bottleneck Analysis

### What Each Module Currently Asks LLM:

#### 1. DECOMPOSE (5 seconds)
**Current LLM Task**:
```
Input: "AI-powered video editor"
LLM Work:
  - Guess business type
  - Guess location
  - Guess target customers (requires research)
  - Estimate price tier (requires market knowledge)
  - SELECT which domains to search
  - INVENT 5-8 search queries

Output: JSON with 8 fields
```

**What Can Move Outside LLM**:
- ❌ Business type detection → Use keyword matching (instant)
- ❌ Location guessing → Ask user or leave empty (instant)
- ❌ Target customers → Pre-fetch via Serper + LLM analyzes
- ❌ Price tier → Pre-fetch competitors' pricing + LLM analyzes
- ❌ Domain selection → Use vertical-based rules (instant)
- ❌ Search queries → LLM still needed (synthesis)

**Result**: LLM only answers "analyze these candidates"

---

#### 2. DISCOVER (2 seconds)
**Current LLM Task**:
```
Input: 200 Reddit/Yelp posts
LLM Work:
  - READ all 200 posts
  - FIND patterns
  - GROUP related insights
  - SYNTHESIZE into 8-15 insights
  - CATEGORIZE as pain_point/unmet_want/etc

Output: Categorized insights with quotes
```

**What Can Move Outside LLM**:
- ❌ Post fetching → Already done by Serper
- ❌ Basic filtering → Filter by score/date (instant)
- ❌ Duplicate detection → Use keyword similarity (instant)
- ❌ SYNTHESIS → LLM needed

**Result**: Give LLM only top 50 posts (not 200) + pre-filtered duplicates

---

#### 3. ANALYZE (2 seconds per section)
**Current LLM Task**:
```
Input: Decomposition + selected insight
LLM Work:
  - RESEARCH competitors
  - ANALYZE market size
  - ESTIMATE TAM/SAM
  - SYNTHESIZE risks

Output: Analysis report
```

**What Can Move Outside LLM**:
- ❌ Competitor finding → Serper search (parallel)
- ❌ Market size data → Pre-fetch from sources
- ❌ SYNTHESIS → LLM needed

**Result**: Give LLM curated data + ask for analysis

---

## 3-Phase Implementation

### Phase 1: Preprocessor Service (10 min)
Create `backend/app/services/preprocessor.py`:
- Parallel data fetching (Serper, Reddit, etc.)
- Lightweight local processing
- Return curated data to endpoints

### Phase 2: Parallel Frontend Requests (5 min)
Update `frontend/src/hooks/use-research.ts`:
- Change from sequential to Promise.all()
- Request all modules at once

### Phase 3: Streaming API (15 min)
Add `backend/app/api/research_stream.py`:
- SSE or WebSocket streaming
- Send results as they complete
- Real-time progress updates

---

## Expected Performance Gains

### Current Architecture
```
Decompose (LLM) [5s]
    → Discover (LLM) [2s]
    → Analyze (LLM) [2s]
    → Setup (LLM) [2s]
    → Validate (LLM) [2s]
Total: 13 seconds
```

### After Phase 1 (Preprocessing)
```
Preprocessing (Parallel) [0.5s]
    ├─ Fetch competitors
    ├─ Fetch market data
    └─ Fetch communities
Decompose (LLM, smaller) [2s]
Discover (LLM, smaller) [2s]
Analyze (LLM) [2s]
Setup (LLM) [2s]
Validate (LLM) [2s]
Total: ~5 seconds (3x faster!)
```

### After Phase 2 (Parallel Requests)
```
Decompose (LLM) [2s]
Discover (LLM) [2s]  ├─ All in parallel
Analyze (LLM) [2s]   ├─ Not sequential
Setup (LLM) [2s]     ├─
Validate (LLM) [2s]  ┘
Total: ~2 seconds (7x faster!)
```

### After Phase 3 (Streaming)
User sees results appearing:
- t=0.5s: "Fetching market data..."
- t=1s: ✅ Decompose returned
- t=2s: ✅ Discover returned
- t=3s: ✅ Analyze returned
- t=4s: ✅ Setup returned
- t=5s: ✅ Validate returned

**Perceived speed: 5x faster** (shows progress)

---

## Implementation Checklist

- [ ] Phase 1: Create preprocessor service
- [ ] Phase 1: Update decompose endpoint
- [ ] Phase 1: Update discover endpoint
- [ ] Phase 1: Test and benchmark
- [ ] Phase 2: Update frontend hooks (parallel requests)
- [ ] Phase 2: Test frontend integration
- [ ] Phase 3: Add streaming endpoint
- [ ] Phase 3: Update frontend to consume stream
- [ ] Benchmark final performance
- [ ] Deploy to production

---

## Key Design Principle

**Hierarchy of Processing Speed**:
1. **Instant** (Local processing, keyword matching) - Do first
2. **Fast** (API calls, Serper search) - Do second, in parallel
3. **Slow** (LLM synthesis, analysis) - Do last, in parallel
4. **Stream** (Return results as soon as ready) - Always

**Avoid**:
- ❌ Asking LLM to search (use Serper)
- ❌ Asking LLM to fetch (use APIs)
- ❌ Making requests sequential (use parallel)
- ❌ Making user wait for everything (use streaming)

