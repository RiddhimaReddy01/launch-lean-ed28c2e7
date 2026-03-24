# Lovable Frontend Integration Guide

## Architecture

```
Lovable Frontend
    ↓
[Parallel API Calls]
    ├─ POST /api/decompose-idea
    ├─ POST /api/discover-insights  (parallel)
    ├─ POST /api/analyze-section     (parallel)
    ├─ POST /api/setup               (parallel)
    └─ POST /api/generate-validation (parallel)
    ↓
[Render Primary] → [Ngrok Fallback] (auto-retry on timeout)
    ↓
[Supabase Cache] (results stored for 7 days)
    ↓
Display Results
```

## Implementation: Parallel Tab Processing

### **Frontend Code Pattern (TypeScript/React)**

```typescript
// Call all 5 tabs in PARALLEL - not sequential
async function analyzeIdea(idea: string) {
  const [decompose, discover, analyze, setup, validate] = await Promise.all([
    // Tab 1: Decompose (fast, ~1-2s on Render)
    apiClient.post('/api/decompose-idea', { idea }),

    // Tab 2-5: These depend on decompose, but can start immediately
    // They'll wait for decompose internally
    apiClient.post('/api/discover-insights', { idea }),
    apiClient.post('/api/analyze-section', { idea, section: 'opportunity' }),
    apiClient.post('/api/setup', { idea }),
    apiClient.post('/api/generate-validation', { idea }),
  ]);

  return {
    decompose,
    discover,
    analyze,
    setup,
    validate,
  };
}
```

### **Expected Performance**

| Scenario | Time |
|----------|------|
| Sequential (old way) | 60-80 seconds |
| Parallel (new way) | 15-20 seconds |
| **Speedup** | **4x faster** |
| With Cache Hit | <500ms |

### **How Caching Works**

1. **First request** → API processes all tabs → Results stored in Supabase
2. **Same idea again** → Cached results returned instantly (~500ms)
3. **Cache expires** → 7 days (regenerate on demand)

## Environment Variables

Set these in Lovable settings:

```env
VITE_API_URL=https://launch-lean-ed28c2e7.onrender.com
VITE_API_FALLBACK_URL=https://steven-impervious-lorretta.ngrok-free.dev
VITE_API_PRIMARY_TIMEOUT=5000      # 5 seconds for Render
VITE_API_TIMEOUT=90000             # 90 seconds for Ngrok fallback
```

## Auto-Fallback Logic

```javascript
async function callAPI(endpoint, data) {
  try {
    // Try Render first (fast)
    return await fetch(`${VITE_API_URL}${endpoint}`, {
      timeout: VITE_API_PRIMARY_TIMEOUT,
      ...requestOptions
    });
  } catch (primaryError) {
    console.warn('Primary endpoint failed, trying fallback...');

    // If Render times out, use Ngrok (slow but reliable)
    return await fetch(`${VITE_API_FALLBACK_URL}${endpoint}`, {
      timeout: VITE_API_TIMEOUT,
      ...requestOptions
    });
  }
}
```

## API Endpoints

### **Individual Tab Endpoints** (call in parallel)

```
POST /api/decompose-idea
  Input: { idea: "string" }
  Output: { business_type, location, target_customers, search_queries, ... }

POST /api/discover-insights
  Input: { decomposition: DecomposeResponse }
  Output: { sources, insights, [...] }

POST /api/analyze-section
  Input: { section: "opportunity"|"customers"|"competitors"|"rootcause"|"costs",
           decomposition: DecomposeResponse,
           insight: Insight }
  Output: { section, data: {...} }

POST /api/setup
  Input: { decomposition: DecomposeResponse, insight: Insight }
  Output: { cost_tiers, suppliers, team, timeline, [...] }

POST /api/generate-validation
  Input: { decomposition: DecomposeResponse, insight: Insight, channels?: string[] }
  Output: { risks, validations, mitigation_strategies, [...] }
```

### **Dashboard Endpoints** (for saving ideas)

```
POST /api/ideas
  Save new idea with all research data

GET /api/ideas
  List all user's saved ideas

GET /api/ideas/{id}
  Retrieve specific idea with all data

PATCH /api/ideas/{id}
  Update idea with new research findings
```

## Data Flow Diagram

```
User enters idea
    ↓
[Frontend calls all 5 tabs in parallel]
    ├─ decompose-idea       → 2s
    ├─ discover-insights    → 3s (waits for decompose internally)
    ├─ analyze-section      → 5s (waits for decompose internally)
    ├─ setup                → 2s (waits for decompose internally)
    └─ generate-validation  → 3s (waits for decompose internally)
    ↓
All complete in ~5s total (not 15s sequential)
    ↓
[Results cached in Supabase]
    ↓
[Next time same idea is analyzed → instant 500ms]
    ↓
[User can save idea to Dashboard]
```

## Key Features for Lovable

### ✅ **What's Already Implemented**

1. **Parallel Processing Ready** - Backend supports simultaneous calls
2. **Caching Layer** - Supabase stores results for 7 days
3. **Dashboard CRUD** - Save/view/update all research
4. **Auto-Fallback** - Render → Ngrok on timeout
5. **All 5 Tabs** - Decompose, Discover, Analyze, Setup, Validate

### ⚠️ **What Lovable Needs to Build**

1. **Parallel API orchestration** - Call all tabs at once
2. **Caching UI state** - Show cached vs fresh results
3. **Progress indicators** - Which tabs are loading
4. **Error handling** - Graceful fallback display
5. **Result display** - Format tab results beautifully

## Performance Optimization Tips

1. **Cache aggressively** - Store results locally in frontend
2. **Show progress** - Users see tabs loading in real-time
3. **Debounce calls** - Don't re-analyze if user hasn't changed idea
4. **Lazy load tabs** - Only fetch tab data when user clicks tab
5. **Use Service Worker** - Cache API responses offline

## Testing Checklist

- [ ] All 5 tabs return data (200 OK)
- [ ] Parallel calls complete in ~15-20 seconds
- [ ] Cache returns results in <500ms on repeat
- [ ] Fallback activates when Render is slow
- [ ] Dashboard saves ideas correctly
- [ ] Ideas persist across sessions
- [ ] Decompose results are accurate
- [ ] Discover finds relevant market data

## Support

**Backend Status**: https://launch-lean-ed28c2e7.onrender.com/health

**Primary Backend**: Render (fast, production)
**Fallback Backend**: Ngrok (slow, development)
**Database**: Supabase (PostgreSQL + caching)
**Auth**: Development bypass (no login required for MVP)

---

**Ready to build!** 🚀
