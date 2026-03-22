

## Why tabs appear empty (and the fix)

### What's actually happening

After testing the full flow, **all 4 tabs (Discover, Analyze, Setup, Validate) DO populate correctly**. The "not populated" appearance is caused by two issues:

1. **Loading flash on Analyze tab**: When you first navigate to Analyze, it shows "Nothing yet / No sizing data returned" for 2-3 seconds while the API calls are in flight. Once responses arrive, data renders correctly (TAM $200M, segments, competitors, etc.). The problem is the component shows the empty state instead of a loading skeleton during fetch.

2. **Discover shows "Test insight"**: Your Render backend's `/api/discover-insights` endpoint was returning hardcoded test data. The diff shows you removed that test return, but the backend may not have redeployed yet on Render. Once it redeploys, Discover will show real insights with proper scores.

### Plan

**Fix 1: Show loading skeletons instead of empty states while data is fetching**

In `src/components/analyze/AnalyzeModule.tsx`:
- Each tab section currently renders `EmptyState` when mapped data is `undefined`, but doesn't distinguish between "still loading" and "no data returned"
- Add a check: if the relevant query is still `isFetching` or `isLoading`, show `SectionSkeleton` instead of `EmptyState`
- Apply the same pattern to each render case (sizing, demand, segments, competitors, structure, rootcause, strategic, costs)

In `src/components/setup/SetupModule.tsx`:
- Same fix: show skeleton while `setupQuery.isLoading` instead of "No cost tiers available yet"

**Fix 2: Verify backend redeployment**
- The discover test data removal is already in your diff — just needs Render to pick it up
- No frontend code change needed for this

### Technical details

The root cause is in `AnalyzeModule`'s render logic. For example, the opportunity sizing tab does:
```
view.market ? <OpportunitySizing data={view.market} /> : <EmptyState message="No sizing data" />
```

It should be:
```
sizingQuery.isLoading ? <SectionSkeleton /> : view.market ? <OpportunitySizing ... /> : <EmptyState ... />
```

This pattern applies to all 8 sub-tabs in Analyze and the Setup module tabs. A straightforward change — about 8 conditional updates in AnalyzeModule and 4 in SetupModule.

