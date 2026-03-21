# LaunchLens AI - Backend API

Python FastAPI backend for LaunchLens AI, the startup market research platform.

## Architecture

```
Lovable Frontend (React) ──→ FastAPI Backend ──→ Groq / Gemini (LLM)
                                    │               Reddit .json (data)
                                    │               Serper.dev (Google search)
                                    └──→ Supabase (DB + Auth)
```

## Endpoints

| Endpoint | Purpose | LLM Calls | External Data |
|----------|---------|-----------|---------------|
| `POST /api/decompose-idea` | Parse idea → structured components | 1 | None |
| `POST /api/discover-insights` | Scan sources → ranked insights | 2 | Reddit + Serper |
| `POST /api/analyze-section` | Generate analysis section (per tab) | 1 | Serper (competitors only) |
| `POST /api/generate-setup` | Launch plan with costs + suppliers | 1 | Serper (suppliers) |
| `POST /api/generate-validation` | Landing page + survey + communities | 1 | Serper (communities) |

## Quick Start (Local Development)

```bash
# 1. Clone and enter directory
cd launchlens-backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your API keys (see "API Keys" section below)

# 5. Run the server
uvicorn app.main:app --reload --port 8000

# 6. Open docs
# http://localhost:8000/docs
```

## API Keys (All Free)

| Key | Where to Get | Free Tier |
|-----|-------------|-----------|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) | No credit card. ~30 req/min |
| `GEMINI_API_KEY` | [aistudio.google.com](https://aistudio.google.com) | 15 req/min, 1500 req/day |
| `SERPER_API_KEY` | [serper.dev](https://serper.dev) | 2,500 searches/month |
| `SUPABASE_URL` + keys | [supabase.com](https://supabase.com) | 2 free projects |

## Deploy to Render (Free)

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. Render auto-detects `render.yaml`
5. Add environment variables in the Render dashboard
6. Deploy!

**Cold start note:** Render free tier spins down after 15 min of inactivity.
First request takes ~30s. Pre-cached demo data loads from Supabase (no backend needed).

## Project Structure

```
launchlens-backend/
├── app/
│   ├── main.py                    # FastAPI app, CORS, routes
│   ├── core/
│   │   ├── __init__.py            # Settings (env vars)
│   │   ├── config.py              # Config singleton
│   │   └── auth.py                # Supabase JWT verification
│   ├── services/
│   │   ├── llm_client.py          # Groq/Gemini fallback wrapper
│   │   ├── reddit_scraper.py      # Reddit .json endpoint fetcher
│   │   ├── google_search.py       # Serper.dev search wrapper
│   │   └── data_cleaner.py        # Filtering, dedup, normalization
│   ├── prompts/
│   │   └── templates.py           # All LLM system prompts
│   ├── routes/
│   │   ├── decompose.py           # POST /api/decompose-idea
│   │   ├── discover.py            # POST /api/discover-insights
│   │   ├── analyze.py             # POST /api/analyze-section
│   │   ├── setup.py               # POST /api/generate-setup
│   │   └── validate.py            # POST /api/generate-validation
│   └── schemas/
│       └── models.py              # Pydantic request/response models
├── requirements.txt
├── render.yaml                    # Render deployment config
├── .env.example
└── README.md
```

## Connecting the Lovable Frontend

In your Lovable project, add this environment variable:
```
VITE_API_URL=https://your-render-service.onrender.com
```

Then use this fetch pattern in your frontend services:
```typescript
const API_BASE = import.meta.env.VITE_API_URL;

export async function decomposeIdea(idea: string, token: string) {
  const res = await fetch(`${API_BASE}/api/decompose-idea`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
    },
    body: JSON.stringify({ idea }),
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}
```

## LLM Fallback Chain

Every endpoint uses the same pattern:
1. **Groq** (LLaMA 3.3 70B) — fastest, primary
2. **Gemini Flash** — if Groq rate-limited
3. **503 error** — frontend falls back to cached demo data from Supabase
