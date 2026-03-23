# Complete System Testing Guide

## Setup

### 1. Start Backend
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

Expected output:
```
✅ All required environment variables configured
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 2. Start Frontend (new terminal)
```bash
cd frontend
npm run dev
```

Expected output:
```
  VITE v... ready in ... ms

  ➜  Local:   http://localhost:5173/
```

---

## Test Flow: End-to-End

### Step 1: Authentication (5 min)

**URL:** http://localhost:5173

1. Click "Get Started"
2. Sign up with email: `test@example.com` / password: `Test123!`
3. Verify email sent (check console for email-validator mock)
4. ✅ Redirect to `/research`

**Expected:**
- Auth page loads
- Form validation works
- Token saved to localStorage

---

### Step 2: Complete Research Pipeline (10 min)

**URL:** http://localhost:5173/research

#### DECOMPOSE Tab:
1. Enter business: "AI Writing Assistant"
2. Enter location: "San Francisco, CA"
3. Select customers: "Freelancers, Students"
4. Select pricing: "Low Cost"
5. Click "Continue"

**Expected:**
- Form validation works
- Decomposition data sent to backend
- Loading indicator appears (~3s)
- Moves to DISCOVER tab

#### DISCOVER Tab:
1. View market insights (generated from Reddit + Google)
2. See 8-12 insights with:
   - Type badge (pain_point, unmet_want, etc.)
   - Score (0-10)
   - Evidence quotes
3. Click "Continue"

**Expected:**
- Real API calls to Serper + Reddit
- Caching working (if run 2x)
- Insights ranked by composite score
- Sources count displayed

#### ANALYZE Tab:
1. View 5 analysis sections (lazy-loaded):
   - OPPORTUNITY: TAM/SAM/SOM sizing
   - CUSTOMERS: 3-4 segments
   - COMPETITORS: 4-8 with threat levels
   - ROOT_CAUSE: 3-5 strategic reasons
   - COSTS: budget estimation
2. Click "Continue"

**Expected:**
- Sections load as clicked
- 1-2 second load per section
- Comprehensive data displayed
- No duplicate requests (caching)

#### SETUP Tab:
1. View cost tiers: Starter, Standard, Premium
2. View timeline: 4-6 phases, 12-24 weeks
3. View supplier list: payment processing, hosting, etc.
4. Click "Continue"

**Expected:**
- Multiple cost options
- Realistic timeline
- Relevant suppliers

#### VALIDATE Tab:
1. View landing page copy (from pain points)
2. View 10 communities to target
3. View scorecard targets
4. Click "Save Idea"

**Expected:**
- Landing page uses VERBATIM quotes from Discover
- Communities are relevant (subreddits, forums)
- Scorecard shows realistic targets

---

### Step 3: Save & View Idea (5 min)

**URL:** http://localhost:5173/dashboard (auto-redirect after save)

1. Title appears: "AI Writing Assistant"
2. 5 purple dots (all modules complete)
3. Status badge: "active"
4. Date: "just now"
5. Click card → `/ideas/{id}`

**Expected:**
- Idea saved to database
- All module dots filled
- Dashboard refreshes
- Navigation works

---

### Step 4: Idea Detail Exploration (10 min)

**URL:** http://localhost:5173/ideas/{ideaId}

#### Overview Tab:
- Business Type: "AI Writing Assistant" ✓
- Location: "San Francisco, CA" ✓
- Customers: "Freelancers, Students" ✓
- Price Tier: "Low Cost" ✓
- Module completion: All checked ✓

#### Discover Tab:
- Sources count: Shows actual number ✓
- Top 5 insights: Listed with scores ✓
- Each insight shows type badge ✓

#### Analyze Tab:
- Data displays correctly ✓
- JSON view is readable ✓

#### Setup Tab:
- Cost tiers show ranges ✓
- Timeline shows phases and weeks ✓

#### Validate Tab:
- Landing page headline visible ✓
- 6 communities displayed ✓
- Scorecard shows targets ✓
- "Log New Experiment" button visible ✓

#### Notes Tab:
1. Click "+ Add Notes"
2. Type: "This is a promising market with strong demand signals"
3. Click "Save Notes"
4. Refresh page (F5)
5. Notes still visible ✓

**Expected:**
- All tabs load data correctly
- Tab switching is instant
- No console errors
- Notes persist

---

### Step 5: Validation Experiment Logging (5 min)

**URL:** http://localhost:5173/ideas/{ideaId} → Validate Tab

1. Click "+ Log New Experiment"
2. Check methods:
   - ✓ landing_page
   - ✓ survey
   - ✓ community
3. Enter metrics:
   - Waitlist Signups: 45
   - Survey Completions: 32
   - Would Switch Rate: 72
   - Price Tolerance: 8.50
   - Community Engagement: 18
   - Reddit Upvotes: 156
4. Click "Save & Get Verdict"

**Expected:**
- Form validation works
- Loading spinner appears
- Verdict card appears below:
  - **Verdict:** "GO" (green badge)
  - **Reasoning:** "Strong demand signal..."
  - Shows metric summary

5. Log another experiment with low metrics:
   - Waitlist Signups: 12
   - Survey Completions: 4
   - Would Switch Rate: 25
   - Price Tolerance: 3
   - Community Engagement: 2
   - Reddit Upvotes: 12

**Expected:**
- **Verdict:** "KILL" (red badge)
- **Reasoning:** "Low interest across channels..."

**Verdict Rules:**
- ✅ GO: 50+ signups, 60%+ switch, $8+ price
- ✅ PIVOT: 30-50 signups OR lower switch rate
- ✅ KILL: <30 signups AND <30% switch rate
- ✅ AWAITING: No data entered

---

### Step 6: PDF Export (5 min)

**URL:** http://localhost:5173/ideas/{ideaId}

1. Click "Export PDF" (top right)
2. File downloads: `AI Writing Assistant.pdf`
3. Open PDF in reader

**Expected:**
- File downloads within 3 seconds
- PDF opens without errors
- Contains all research data:
  - Decomposition (business, location, customers)
  - Discoveries (insights with scores)
  - Analysis (all 5 sections)
  - Setup (tiers, timeline)
  - Validate (toolkit + experiments)
- Professional formatting
- No missing content

---

### Step 7: Delete Idea (2 min)

**URL:** http://localhost:5173/ideas/{ideaId}

1. Click "Delete" (top right)
2. Confirm in dialog
3. Redirects to `/dashboard`

**Expected:**
- Confirmation dialog appears
- Idea removed from database
- Dashboard refreshes
- Idea card no longer visible
- Can verify with GET /api/ideas

---

### Step 8: Dashboard Management (5 min)

**URL:** http://localhost:5173/dashboard

1. Create 3 more ideas (repeat Step 2-3)
2. Dashboard shows 3 cards in grid
3. Each shows correct:
   - Title ✓
   - Date (relative: "moments ago", "2 minutes ago") ✓
   - Module dots (filled/empty per completion) ✓
   - Status badges ✓
   - Tags (max 2 + count) ✓
4. Click "New Analysis" → `/research` ✓
5. Click "Saved" nav link → `/dashboard` ✓
6. Click "Logout" → `/auth` ✓

**Expected:**
- Grid is responsive (auto-fill)
- Hover effects work (shadow, translateY)
- Navigation works bidirectionally
- All data persists

---

## API Testing (Optional)

### List Ideas
```bash
curl -H "Authorization: Bearer {token}" http://localhost:8000/api/ideas
```

**Expected Response:**
```json
[
  {
    "id": "uuid",
    "title": "AI Writing Assistant",
    "status": "active",
    "created_at": "2026-03-22T...",
    "has_decompose": true,
    "has_discover": true,
    "has_analyze": true,
    "has_setup": true,
    "has_validate": true,
    "tags": []
  }
]
```

### Get Validation Experiments
```bash
curl -H "Authorization: Bearer {token}" http://localhost:8000/api/validation-experiments/{idea_id}
```

**Expected Response:**
```json
{
  "experiments": [
    {
      "id": "uuid",
      "idea_id": "uuid",
      "methods": ["landing_page", "survey"],
      "waitlist_signups": 45,
      "verdict": "go",
      "reasoning": "Strong demand signal...",
      "created_at": "2026-03-22T..."
    }
  ],
  "count": 1
}
```

---

## Performance Validation

### Metrics to Check:
- **Dashboard load:** <1s (with caching)
- **Tab switch:** <100ms (instant)
- **Idea fetch:** <500ms
- **Experiment submit:** <2s (includes LLM call for verdict)
- **PDF export:** <3s
- **No Console Errors:** 0 ❌

### Browser DevTools:
1. Open DevTools (F12)
2. Go to Network tab
3. Check each action:
   - API calls complete successfully
   - Response times are reasonable
   - No 4xx/5xx errors
   - No blocked resources

4. Go to Console tab
5. Check for errors/warnings:
   - Should see 0 errors
   - May see 1-2 deprecation warnings (from deps)

---

## Troubleshooting

### Issue: API 401 (Unauthorized)
**Solution:** Check token in localStorage
```js
localStorage.getItem('auth_token')
```
Should return a valid JWT. If not, re-authenticate.

### Issue: PDF Export fails
**Solution:** Check backend logs for export errors
```
backend/app/api/export.py
```
Ensure all data is properly formatted.

### Issue: Experiments not saving
**Solution:** Check database connection
```
SUPABASE_URL, SUPABASE_ANON_KEY
```
Should be set in `.env`

### Issue: Tab content not loading
**Solution:** Check API endpoint availability
```bash
curl http://localhost:8000/api/ideas/{id}
```
Should return full idea data.

---

## Sign-Off Checklist

- [ ] Authentication works (sign up, sign in, logout)
- [ ] Research pipeline completes all 5 tabs
- [ ] Dashboard displays ideas grid
- [ ] Idea detail shows all 6 tabs
- [ ] Validation experiments log and show verdicts
- [ ] Notes save and persist
- [ ] PDF export works
- [ ] Delete idea works
- [ ] Navigation is bidirectional
- [ ] No console errors
- [ ] API calls complete <2s
- [ ] Responsive on mobile (375px width)
- [ ] Logout removes auth token

**Status:** ✅ Ready for Production

---

## Additional Resources

- Backend API docs: http://localhost:8000/docs
- Deployment guide: `DEPLOYMENT_GUIDE.md`
- Backend architecture: `BACKEND_ARCHITECTURE.md`
- Validate tab details: `VALIDATE_TAB_GUIDE.md`
