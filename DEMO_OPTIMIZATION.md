# Demo Optimization: Senior Engineer Architecture

## Problem Statement
Current pipeline is over-engineered for demos:
- Each endpoint makes 1-2 LLM calls
- 5 endpoints = 5-10 LLM calls total = 30-60 seconds
- Multiple API calls (Reddit, Google, LLM)
- Scattered fallback logic
- No caching between endpoints

## Solution: Senior Engineer Pipeline Redesign

### Architecture Changes

#### 1. DECOMPOSE (Current: 4-5s → Optimized: <100ms)
**Before:**
```python
idea → LLM extraction → normalize → response
```

**After:**
```python
idea → extract via heuristics + demo cache → response
```

**Implementation:**
- Use pattern matching for common ideas (juice bar, SaaS, marketplace)
- Add `demo.py` service with pre-built decompositions
- Instant response for known ideas
- Smart heuristics for unknown ideas (no LLM needed)

**Benefit:** Decompose is deterministic, not random. No value in LLM here.

---

#### 2. DISCOVER (Current: 8-10s → Optimized: 2-3s)
**Before:**
```python
Reddit fetch (timeout) → Google fetch (timeout) → clean → merge → LLM analysis
```

**After:**
```python
Demo cache check → [Reddit || Google] in parallel with fallback → use fallback insights
```

**Implementation:**
- Check demo cache first (instant)
- Parallel Reddit + Google fetch (no sequential waiting)
- Use fallback keyword analysis (instant, no LLM)
- Cache results for this session

**Benefit:** Fallback insights are actually good enough and fast.

---

#### 3. ANALYZE (Current: 3 calls, 12-15s → Optimized: 1 call, 4-5s)
**Before:**
```python
opportunity section → LLM → response
competitors section → LLM → response
customers section → LLM → response
```

**After:**
```python
all 3 sections → SINGLE batched LLM call → split response → 3 outputs
```

**Implementation:**
- Combine opportunity + competitors + customers into ONE prompt
- Parse response and split into 3 result objects
- LLM works faster on longer context (fewer stops/starts)

**Benefit:** 3 LLM calls → 1 LLM call = 3x speedup.

---

#### 4. SETUP (Current: 2-3s LLM → Optimized: <100ms template)
**Before:**
```python
business type → LLM → generate costs, timeline, team
```

**After:**
```python
template → fill with values from decompose → return
```

**Implementation:**
- Pre-built cost/timeline templates per business type
- Replace placeholders with actual values
- No LLM needed (deterministic data)

**Cost templates:**
```python
MVP_TEMPLATE = {
  "food": {"min": 15000, "max": 25000},
  "saas": {"min": 8000, "max": 15000},
  "marketplace": {"min": 20000, "max": 35000},
}
```

**Benefit:** Setup is structure + examples, not creative. No LLM value.

---

#### 5. VALIDATE (Current: 2-3s LLM → Optimized: demo data)
**Before:**
```python
Generate landing page copy → generate communities → generate scorecard (all LLM)
```

**After:**
```python
Use pre-built toolkit + demo data → return
```

**Implementation:**
- Validate toolkit is mostly static (landing page templates, community lists)
- Use demo experiments data for demo
- Real users can log their own experiments

**Benefit:** Validate is about framework, not generation. Static data works.

---

### New Architecture Diagram

```
USER SUBMITS IDEA
    ↓
DECOMPOSE (check demo cache → heuristics) ✓ <100ms
    ↓ (passes business_type to all downstream)
    ├─→ DISCOVER (demo cache → parallel APIs → fallback) ✓ 2-3s
    ├─→ ANALYZE (batched LLM call) ✓ 4-5s
    ├─→ SETUP (template fill) ✓ <100ms
    └─→ VALIDATE (demo toolkit) ✓ <100ms
        ↓
TOTAL DEMO PIPELINE: 6-10 seconds
(Currently: 30-60 seconds)
```

---

## Implementation Checklist

### Phase 1: Add Demo Service ✅
- [x] Create `app/services/demo.py` with demo ideas
- [x] Pre-build JSON for juice bar, SaaS, marketplace examples

### Phase 2: Optimize Decompose
- [ ] Modify `app/api/decompose.py` to check demo cache first
- [ ] Remove LLM call (use heuristics + cache only)
- [ ] Add extraction functions for heuristics

### Phase 3: Optimize Discover
- [ ] Already uses fallback! Keep as-is
- [ ] Verify parallel fetching of Reddit + Google
- [ ] Cache results by business_type

### Phase 4: Optimize Analyze
- [ ] Modify `app/api/analyze.py`
- [ ] Batch all 3 sections into one LLM call
- [ ] Parse and split response into 3 outputs

### Phase 5: Optimize Setup
- [ ] Replace `app/api/setup.py` LLM call with templates
- [ ] Add template fill logic
- [ ] Return instant response

### Phase 6: Optimize Validate
- [ ] Replace `app/api/validate.py` LLM calls with static toolkit
- [ ] Add demo experiment data
- [ ] Return instant response

---

## Why Senior Engineers Do This

1. **Understand the problem domain**
   - Decomposition is structural (no LLM needed)
   - Setup is templated (no LLM needed)
   - Validate is framework (no LLM needed)

2. **Eliminate waste**
   - Remove LLM calls where they don't add value
   - Batch calls where they can be combined
   - Use fallbacks that work well

3. **Think from user perspective**
   - 30-60 seconds is too slow for demo
   - 6-10 seconds is conversational
   - Instant results feel snappy

4. **Prioritize simplicity**
   - Less code = fewer bugs
   - Templates are easier to maintain
   - Demo data is predictable

---

## Expected Improvements

| Endpoint | Before | After | Speedup |
|----------|--------|-------|---------|
| Decompose | 4-5s | <100ms | 40-50x |
| Discover | 8-10s | 2-3s | 3-5x |
| Analyze | 12-15s | 4-5s | 3x |
| Setup | 2-3s | <100ms | 20-30x |
| Validate | 2-3s | <100ms | 20-30x |
| **TOTAL** | **30-60s** | **6-10s** | **5-6x** |

---

## Demo Script

```
1. User enters: "AI tutoring platform for high school students"

2. DECOMPOSE (instant)
   - Extract: business_type, location, customers
   - Return in <100ms

3. DISCOVER (2-3s)
   - Show: Market pain points from Reddit + Google
   - Display: "Finding insights from students and parents..."

4. ANALYZE (4-5s)
   - Show: Market size, competitors, customer segments
   - Display: "Analyzing market opportunity..."

5. SETUP (instant)
   - Show: Costs, timeline, team structure
   - Return in <100ms

6. VALIDATE (instant)
   - Show: Landing page templates, communities to reach
   - Return in <100ms

TOTAL: ~10 seconds for complete research pipeline
```

---

## Production Considerations

- Demo mode can stay for presentations
- Real users get full LLM mode
- Add `?demo=true` flag to force demo mode
- Keep actual LLM calls for serious analysis
- Monitor which ideas get demo vs real processing

