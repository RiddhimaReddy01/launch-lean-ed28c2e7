# Lovable Implementation Spec

## 1. Parallel API Calls on Submit ✅

**When user clicks "Analyze Idea":**

```typescript
async function handleAnalyzeIdea(idea: string) {
  setLoading(true);

  // FIRE ALL 5 CALLS IMMEDIATELY IN PARALLEL
  const promises = [
    api.post('/api/decompose-idea', { idea }),
    api.post('/api/discover-insights', { idea }),
    api.post('/api/analyze-section', { idea, section: 'opportunity' }),
    api.post('/api/setup', { idea }),
    api.post('/api/generate-validation', { idea }),
  ];

  try {
    const [decompose, discover, analyze, setup, validate] = await Promise.all(promises);

    // All 5 completed in parallel
    setResults({ decompose, discover, analyze, setup, validate });
  } catch (error) {
    // Handle failure
  } finally {
    setLoading(false);
  }
}
```

**Timeline:**
- t=0s: All 5 calls fire simultaneously
- t=2s: Decompose completes (needed by others)
- t=3s: Discover completes (parallel with others)
- t=5s: Analyze, Setup, Validate complete
- t=5s: All results ready to display

---

## 2. Use Existing result_cache Table ✅

**Instead of creating new table, UPDATE the existing one:**

```sql
-- Your existing result_cache table
-- Add columns for the 5 tabs if they don't exist

ALTER TABLE result_cache ADD COLUMN IF NOT EXISTS decompose JSONB;
ALTER TABLE result_cache ADD COLUMN IF NOT EXISTS discover JSONB;
ALTER TABLE result_cache ADD COLUMN IF NOT EXISTS analyze JSONB;
ALTER TABLE result_cache ADD COLUMN IF NOT EXISTS setup JSONB;
ALTER TABLE result_cache ADD COLUMN IF NOT EXISTS validate JSONB;

-- Index for fast lookups
CREATE INDEX IF NOT EXISTS idx_result_cache_idea_hash
  ON result_cache(idea_hash);
```

**Cache Lookup Before Submitting:**

```typescript
async function handleAnalyzeIdea(idea: string) {
  const ideaHash = hashIdea(idea); // md5 hash of idea

  // CHECK CACHE FIRST
  const cached = await api.get(`/api/ideas/cache/${ideaHash}`);
  if (cached) {
    console.log('✅ Cache hit! Using stored results');
    setResults(cached);
    return; // Skip API calls
  }

  console.log('❌ Cache miss - fetching fresh data');

  // No cache → Fire all 5 calls
  const [decompose, discover, analyze, setup, validate] = await Promise.all([
    api.post('/api/decompose-idea', { idea }),
    api.post('/api/discover-insights', { idea }),
    api.post('/api/analyze-section', { idea, section: 'opportunity' }),
    api.post('/api/setup', { idea }),
    api.post('/api/generate-validation', { idea }),
  ]);

  // Store in Supabase for next time
  await api.post('/api/ideas/cache', {
    idea_hash: ideaHash,
    decompose, discover, analyze, setup, validate
  });

  setResults({ decompose, discover, analyze, setup, validate });
}
```

---

## 3. Per-Tab Skeleton Loading Experience ✅

**Show skeleton loaders for each tab while loading:**

```tsx
export function ResearchTabs({ results, loading }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">

      {/* TAB 1: DECOMPOSE */}
      <div className="card">
        <h3>Decompose</h3>
        {loading ? (
          <DecomposeSkeleton /> // Show placeholder
        ) : (
          <DecomposeContent data={results.decompose} />
        )}
      </div>

      {/* TAB 2: DISCOVER */}
      <div className="card">
        <h3>Discover</h3>
        {loading ? (
          <DiscoverSkeleton /> // Show placeholder
        ) : (
          <DiscoverContent data={results.discover} />
        )}
      </div>

      {/* TAB 3: ANALYZE */}
      <div className="card">
        <h3>Analyze</h3>
        {loading ? (
          <AnalyzeSkeleton /> // Show placeholder
        ) : (
          <AnalyzeContent data={results.analyze} />
        )}
      </div>

      {/* TAB 4: SETUP */}
      <div className="card">
        <h3>Setup</h3>
        {loading ? (
          <SetupSkeleton /> // Show placeholder
        ) : (
          <SetupContent data={results.setup} />
        )}
      </div>

      {/* TAB 5: VALIDATE */}
      <div className="card">
        <h3>Validate</h3>
        {loading ? (
          <ValidateSkeleton /> // Show placeholder
        ) : (
          <ValidateContent data={results.validate} />
        )}
      </div>

    </div>
  );
}
```

**Skeleton Component Example:**

```tsx
function DecomposeSkeleton() {
  return (
    <div className="space-y-3">
      <Skeleton className="h-4 w-3/4" /> {/* business type */}
      <Skeleton className="h-4 w-1/2" /> {/* target customers */}
      <Skeleton className="h-4 w-2/3" /> {/* pricing */}
      <div className="space-y-2">
        <Skeleton className="h-3 w-full" />
        <Skeleton className="h-3 w-full" />
        <Skeleton className="h-3 w-4/5" />
      </div>
    </div>
  );
}
```

**Progress States:**

```
Initial: "Enter your business idea..."
         [Input field]
         [Analyze Button]

Loading (t=0-5s):
  ┌──────────────┬──────────────┬──────────────┐
  │ Decompose    │ Discover     │ Analyze      │
  │ ▮▮▮▮░░░░░░  │ ▮▮░░░░░░░░░░ │ ░░░░░░░░░░░░ │
  │ 40% complete │ 20% complete │ 0% complete  │
  └──────────────┴──────────────┴──────────────┘

Completed (t=5s):
  ┌──────────────┬──────────────┬──────────────┐
  │ ✅ Decompose │ ✅ Discover  │ ✅ Analyze   │
  │ Business... │ Market... │ Opportunity... │
  └──────────────┴──────────────┴──────────────┘

Cache Hit (t=0.5s):
  ✅ "Using cached results from 2 days ago"
  [Display results instantly]
```

---

## Complete Flow

```
1. USER SUBMITS IDEA
   ↓
2. CHECK CACHE (query result_cache by idea_hash)
   ├─ HIT: Display cached results immediately
   └─ MISS: Continue to step 3
   ↓
3. SHOW 5 SKELETONS (empty cards with placeholder loading bars)
   ↓
4. FIRE ALL 5 API CALLS IN PARALLEL
   api.post('/api/decompose-idea')        ─┐
   api.post('/api/discover-insights')     ─┤
   api.post('/api/analyze-section')       ─┼─ All at t=0
   api.post('/api/setup')                 ─┤
   api.post('/api/generate-validation')   ─┘
   ↓
5. RESULTS ARRIVE (t=5-15s depending on Render vs Ngrok)
   ├─ Decompose:    2s (fastest)
   ├─ Discover:     3s (parallel)
   ├─ Analyze:      5s (LLM call)
   ├─ Setup:        2s (fast)
   └─ Validate:     3s (LLM call)
   ↓
6. UPDATE CACHE (store in result_cache table)
   ↓
7. HIDE SKELETONS, SHOW REAL DATA
   ↓
8. USER CAN SAVE TO DASHBOARD
   POST /api/ideas with all research data
```

---

## State Management

```typescript
interface ResearchState {
  idea: string;
  loading: boolean;
  loadingProgress: { [key: string]: number }; // 0-100%
  results: {
    decompose: DecomposeResponse | null;
    discover: DiscoverResponse | null;
    analyze: AnalyzeResponse | null;
    setup: SetupResponse | null;
    validate: ValidateResponse | null;
  };
  error: string | null;
  fromCache: boolean;
  cachedAt: Date | null;
}
```

---

## Key Points

✅ **All 5 calls fire immediately** on submit button click
✅ **Cache checked first** - instant results if available
✅ **Per-tab skeletons** - shows progress for each tab
✅ **Parallel execution** - 5s total (not 60s sequential)
✅ **Results stored** - next analysis of same idea is <500ms
✅ **Dashboard integration** - save all research to idea

---

## Backend API Endpoints Needed

```
1. POST /api/decompose-idea
2. POST /api/discover-insights
3. POST /api/analyze-section
4. POST /api/setup
5. POST /api/generate-validation
6. POST /api/ideas (save to dashboard)
7. GET /api/ideas/cache/{idea_hash} (check cache)
8. POST /api/ideas/cache (store cache)
```

All ready! ✅
