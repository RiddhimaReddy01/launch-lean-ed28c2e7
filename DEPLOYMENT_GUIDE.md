# LaunchLens Deployment Guide

## Quick Start (5 Minutes)

### 1. Prerequisites
```bash
# Install required tools
- Python 3.11+
- Node.js 18+
- npm/yarn
- Git
```

### 2. Clone Repository
```bash
git clone https://github.com/RiddhimaReddy01/launch-lean-ed28c2e7
cd launch-lean-ed28c2e7
```

### 3. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy .env template
cp .env.example .env
# Edit .env with your API keys (see section 4)
```

### 4. Frontend Setup
```bash
cd frontend
npm install
npm run build  # Verify zero errors
```

### 5. Start Locally
```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

Visit: `http://localhost:5173` (frontend) and `http://localhost:8000/docs` (API docs)

---

# DETAILED DEPLOYMENT GUIDE

## Phase 1: Environment Setup

### 1.1 Database (Supabase)

**Create Supabase Project:**
```bash
1. Go to https://supabase.com
2. Create new project
3. Wait for database initialization (2-3 min)
4. Copy credentials:
   - SUPABASE_URL: Project Settings → API
   - SUPABASE_SERVICE_KEY: Project Settings → API → Service Role Key
```

**Initialize Database:**
```bash
# Run migrations from supabase/migrations/
1. Go to Supabase dashboard
2. SQL Editor
3. Copy-paste each migration file and execute
4. Or use: supabase db push (with local setup)
```

**Create Tables:**
```sql
-- ideas table
CREATE TABLE ideas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    title TEXT NOT NULL,
    business_type TEXT,
    location JSONB,
    decomposition JSONB,
    discover_insights JSONB,
    analyze_sections JSONB,
    setup_data JSONB,
    validation JSONB,
    status TEXT DEFAULT 'in_progress',
    current_tab INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);

-- decompose_cache table
CREATE TABLE decompose_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    idea TEXT NOT NULL UNIQUE,
    output JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT now(),
    expires_at TIMESTAMP DEFAULT now() + INTERVAL '24 hours'
);

-- discover_cache table
CREATE TABLE discover_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_type TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    output JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT now(),
    expires_at TIMESTAMP DEFAULT now() + INTERVAL '7 days',
    UNIQUE(business_type, city, state)
);

-- search_cache table
CREATE TABLE search_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query TEXT NOT NULL,
    api_source TEXT,
    results JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT now(),
    expires_at TIMESTAMP DEFAULT now() + INTERVAL '7 days'
);

-- users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    auth_token TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT now()
);
```

### 1.2 API Keys

**Required Keys:**

| Service | Key Name | Where to Get | Cost |
|---------|----------|-------------|------|
| **Groq** | GROQ_API_KEY | https://console.groq.com | Free (100 req/day) or Paid |
| **Gemini** | GEMINI_API_KEY | https://makersuite.google.com/app/apikey | Free (60 req/min) |
| **OpenRouter** | OPENROUTER_API_KEY | https://openrouter.ai | Free trial |
| **HuggingFace** | HF_API_TOKEN | https://huggingface.co/settings/tokens | Free |
| **Serper** | SERPER_API_KEY | https://serper.dev | $5 for 100 queries |
| **Tavily** | TAVILY_API_KEY | https://tavily.com | Free (1000 credits/month) |
| **Supabase** | SUPABASE_URL, SUPABASE_SERVICE_KEY | Supabase dashboard | Free tier |

**Recommended Setup (Lowest Cost):**
```
- Groq: Paid tier ($5-20/month) - Primary LLM
- Gemini: Free - Fallback
- OpenRouter: Free trial - Fallback
- Serper: Paid ($5/month) - 100 search queries
- Tavily: Free - Search fallback (1000/month)
- HuggingFace: Free - LLM fallback
```

**Total Monthly Cost: ~$10-25**

### 1.3 Create .env File

```bash
# backend/.env
# ═══ LLM PROVIDERS ═══
GROQ_API_KEY=gsk_your_groq_key_here
GEMINI_API_KEY=AIzaSy_your_gemini_key_here
OPENROUTER_API_KEY=sk-or-v1_your_openrouter_key_here
HF_API_TOKEN=hf_your_huggingface_token_here

# ═══ SEARCH APIs ═══
SERPER_API_KEY=your_serper_key_here
TAVILY_API_KEY=your_tavily_key_here

# ═══ DATABASE ═══
SUPABASE_URL=https://your_project.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGc... (your service key)

# ═══ APPLICATION ═══
FRONTEND_URL=http://localhost:5173  # Change for production
ENVIRONMENT=development  # or 'production'
LOG_LEVEL=INFO
```

---

## Phase 2: Backend Deployment

### 2.1 Option A: Render (Recommended for beginners)

**Step 1: Connect Repository**
```bash
1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Connect GitHub (authorize Render)
4. Select repository: launch-lean-ed28c2e7
5. Click "Connect"
```

**Step 2: Configure**
```
Name: launchlens-backend
Environment: Python 3
Root Directory: backend
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Step 3: Add Environment Variables**
```
1. Settings → Environment
2. Add all keys from .env file
3. FRONTEND_URL: https://your-frontend-domain.com
```

**Step 4: Deploy**
```
Click "Create Web Service"
Wait 2-5 minutes for build and deployment
```

**Verification:**
```bash
curl https://your-backend-url/api/health
# Should return: {"status": "ok"}
```

### 2.2 Option B: Railway

**Step 1: Create Project**
```bash
1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub"
4. Choose repository
```

**Step 2: Configure**
```
Service: Python
Root: backend
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Step 3: Add Variables**
```
Settings → Variables
Add all .env keys
```

**Step 4: Deploy**
```
Auto-deploys on git push
Takes 3-5 minutes
```

### 2.3 Option C: Docker (Advanced)

**Create Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build & Push:**
```bash
docker build -t launchlens-backend .
docker tag launchlens-backend:latest YOUR_REGISTRY/launchlens-backend:latest
docker push YOUR_REGISTRY/launchlens-backend:latest
```

**Deploy to Cloud Run (Google):**
```bash
gcloud run deploy launchlens-backend \
  --image YOUR_REGISTRY/launchlens-backend:latest \
  --platform managed \
  --region us-central1 \
  --set-env-vars GROQ_API_KEY=$GROQ_API_KEY,SUPABASE_URL=$SUPABASE_URL,...
```

---

## Phase 3: Frontend Deployment

### 3.1 Option A: Vercel (Recommended for Next.js/Vite)

**Step 1: Deploy**
```bash
1. Go to https://vercel.com
2. Click "New Project"
3. Import GitHub repository
4. Select project: launch-lean-ed28c2e7
5. Root Directory: frontend
```

**Step 2: Environment Variables**
```
VITE_API_URL=https://your-backend-url.com
```

**Step 3: Deploy**
```
Click "Deploy"
Auto-generates domain: your-project.vercel.app
```

### 3.2 Option B: Netlify

**Step 1: Deploy**
```bash
1. Go to https://netlify.com
2. "Connect to Git"
3. Choose repository
```

**Step 2: Configure**
```
Base directory: frontend
Build command: npm run build
Publish directory: dist
```

**Step 3: Environment Variables**
```
VITE_API_URL=https://your-backend-url.com
```

**Step 4: Deploy**
```
Click "Deploy"
Auto-generates domain
```

### 3.3 Option C: Lovable (Special for this app)

**Step 1: Create Lovable Project**
```bash
1. Go to https://lovable.dev
2. Create new project
3. Connect GitHub to sync code
4. Set root: frontend
```

**Step 2: Copy Frontend Code**
```
From: frontend/src/
To: Lovable project editor
```

**Step 3: Set Environment**
```
VITE_API_URL=https://your-backend-url.com
```

**Step 4: Deploy**
```
Click "Deploy"
Uses ~1-2 credits
```

---

## Phase 4: Final Configuration

### 4.1 Connect Frontend to Backend

**Update Frontend API URL:**
```
frontend/.env.production
VITE_API_URL=https://your-backend-url.com
```

**Rebuild:**
```bash
cd frontend
npm run build
```

### 4.2 CORS Configuration (Backend)

**File: backend/app/main.py**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Local dev
        "https://your-frontend-domain.com",  # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4.3 Health Checks

**Backend:**
```bash
curl https://your-backend-url.com/api/health
# Response: {"status": "ok"}
```

**Database:**
```bash
# Check Supabase dashboard
- Tables exist
- No errors in logs
```

---

## Phase 5: Testing Deployment

### 5.1 Test Complete Flow

**Test Endpoint:**
```bash
curl -X POST https://your-backend-url.com/api/decompose-idea \
  -H "Content-Type: application/json" \
  -d '{"idea": "meal prep delivery service in Austin"}'
```

**Expected Response (2-5 seconds):**
```json
{
  "business_type": "meal prep delivery service",
  "location": {"city": "Austin", "state": "TX"},
  "target_customers": ["busy professionals"],
  ...
}
```

### 5.2 End-to-End User Flow

```bash
1. Open https://your-frontend-domain.com
2. Click "Get Started"
3. Sign up / Login
4. Enter idea: "A sustainable meal prep delivery service for busy professionals in Austin Texas"
5. Click "Analyze Idea"
6. Watch all 5 tabs complete:
   ✓ TAB 1 (DECOMPOSE): 3-5s
   ✓ TAB 2 (DISCOVER): 8-12s
   ✓ TAB 3 (ANALYZE): 3-15s per section
   ✓ TAB 4 (SETUP): ~5s
   ✓ TAB 5 (VALIDATE): 7-11s
7. Click "Save to Dashboard"
8. Go to Dashboard, verify idea saved
9. Click idea card, verify all data loads
```

### 5.3 Check Logs

**Render Logs:**
```
1. Go to Render dashboard
2. Select service
3. Logs tab
4. Watch in real-time as requests come in
```

**Supabase Logs:**
```
1. Supabase dashboard
2. Logs section
3. Check for errors/warnings
```

---

## Phase 6: Production Setup

### 6.1 Custom Domain

**For Backend (Render):**
```
1. Settings → Custom Domain
2. Enter domain: api.yoursite.com
3. Add DNS records
4. Wait 5-10 minutes for SSL
```

**For Frontend (Vercel):**
```
1. Settings → Domains
2. Add custom domain
3. Follow DNS setup
```

### 6.2 SSL/HTTPS

**Automatically handled by:**
- Vercel (free)
- Render (free)
- Netlify (free)
- Lovable (included)

### 6.3 Scaling

**If slow responses:**
```
Render:
1. Settings → Instance Type
2. Upgrade from Free to Starter ($7/month)

Railway:
1. Settings → Build & Deploy
2. Increase resources
```

### 6.4 Monitoring

**Setup Error Tracking (Sentry):**
```bash
1. Create account at https://sentry.io
2. Create project for Python
3. Add to backend/requirements.txt:
   sentry-sdk

4. Add to backend/.env:
   SENTRY_DSN=your_sentry_dsn

5. In app/main.py:
   import sentry_sdk
   sentry_sdk.init(os.getenv("SENTRY_DSN"))
```

**Setup Analytics (Posthog):**
```bash
Frontend analytics automatically captured if using Vercel/Netlify
```

---

## Phase 7: Troubleshooting

### Issue: Backend returns 503 Service Unavailable

**Cause:** LLM provider rate-limited

**Solution:**
```bash
1. Check .env has paid Groq key
2. Verify OpenRouter fallback key works
3. Check Supabase is running
4. Restart backend service
```

**Test LLM:**
```bash
curl -X POST https://your-backend-url.com/api/decompose-idea \
  -H "Content-Type: application/json" \
  -d '{"idea": "test idea"}'

If fails: Check Groq API status
```

### Issue: Frontend can't reach backend

**Cause:** CORS or URL mismatch

**Solution:**
```bash
1. Check VITE_API_URL in frontend .env.production
2. Verify backend URL is correct
3. Check CORS settings in backend/app/main.py
4. Clear browser cache
```

**Test Connection:**
```bash
# In browser console:
fetch('https://your-backend-url.com/api/health').then(r => r.json()).then(console.log)
```

### Issue: Database connection fails

**Cause:** Wrong credentials or down

**Solution:**
```bash
1. Verify SUPABASE_URL and SUPABASE_SERVICE_KEY in .env
2. Check Supabase dashboard - is project running?
3. Test connection:
   psql postgresql://user:pass@db.supabase.co:5432/postgres
```

### Issue: Search API rate-limited

**Cause:** Serper quota exceeded

**Solution:**
```bash
1. Check Serper dashboard for usage
2. Upgrade plan ($5/month = 100 → 1000 queries)
3. Tavily fallback kicks in automatically
```

---

## Phase 8: Post-Deployment Checklist

```bash
✓ Backend deployed and responding
✓ Frontend deployed and loads
✓ Frontend can reach backend API
✓ All environment variables set
✓ Database tables created
✓ Supabase auth configured
✓ All 5 API endpoints tested:
  ✓ POST /api/decompose-idea
  ✓ POST /api/discover-insights
  ✓ POST /api/analyze-section
  ✓ POST /api/setup
  ✓ POST /api/generate-validation
✓ End-to-end user flow tested
✓ Error logging configured (Sentry)
✓ Custom domain configured
✓ SSL/HTTPS verified
✓ Backups enabled (Supabase)
✓ Monitor logs for 24 hours
```

---

## Phase 9: Cost Breakdown (Monthly)

### Minimum Cost Setup ($10/month)
```
Render Backend:     Free tier (0.5 CPU, 512MB RAM)
Vercel Frontend:    Free tier
Supabase:           Free tier (500MB storage)
Groq API:           Free tier (100 req/day) or $5
Serper Search:      $5 (100 queries)
Total:              ~$10/month (if Groq paid tier used)
```

### Mid-Scale Setup ($50/month)
```
Render Backend:     Starter tier ($7/month)
Vercel Frontend:    Pro tier ($20/month)
Supabase:           Pro tier ($25/month)
Groq API:           Paid tier usage
Serper Search:      Paid tier ($15/month for 1000 queries)
Total:              ~$70/month
```

### Production Setup ($200+/month)
```
Render Backend:     Standard tier ($30/month)
Vercel Frontend:    Pro tier ($20/month)
Supabase:           Business tier ($100/month)
Groq API:           Usage-based
Serper Search:      Enterprise tier
Additional:         CDN, monitoring, backups
Total:              $200+/month
```

---

## Phase 10: Continuous Deployment

### Auto-Deploy on Git Push

**Render:**
```
Automatically redeploys when you push to main
```

**Vercel:**
```
Automatically redeploys on push to main
```

**Update Process:**
```bash
1. Make changes locally
2. Test: npm run build (frontend), run tests (backend)
3. git add, git commit, git push
4. Auto-deployment triggers
5. Check deployment status in dashboard
6. Verify health endpoints
7. Test frontend/backend
```

---

## Summary: 3 Deployment Paths

### Path 1: Quickest (Render + Vercel)
```
Time: 15 minutes
Cost: $10-20/month
Steps:
1. Deploy backend to Render (5 min)
2. Deploy frontend to Vercel (5 min)
3. Connect URLs (2 min)
4. Test (3 min)
```

### Path 2: Free Trial
```
Time: 10 minutes
Cost: $0 (free tier)
Limits: Rate limits, storage limits
Steps:
1. Deploy to Render free tier
2. Deploy to Vercel free tier
3. Use Groq free tier (100 req/day)
4. Expect slow responses at scale
```

### Path 3: Lovable Full-Stack
```
Time: 20 minutes
Cost: 3 credits (for first deploy)
Steps:
1. Create Lovable project
2. Copy frontend code
3. Set API_URL
4. Deploy (uses 1-2 credits)
5. Backend on Render separately
```

---

## Need Help?

```
Error with Groq? → Check API key and tier at console.groq.com
Error with Supabase? → Check dashboard for errors/logs
Error with frontend? → Check browser console for errors
Error with deployment? → Check service dashboard logs
```

**Deployment successful! 🚀**
