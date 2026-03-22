"""
LaunchLens AI - Backend API
FastAPI application with CORS, route registration, and health check.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.router import router

# ── Logging ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ── App ──
app = FastAPI(
    title="LaunchLens AI API",
    description="Backend API for LaunchLens AI - startup market research platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──
# Allow the Lovable frontend and local development
origins = [
    settings.FRONTEND_URL,
    # Local development
    "http://localhost:8080",    # Vite dev server
    "http://localhost:5173",    # Alternative Vite port
    "http://localhost:3000",    # Alternative dev port
    "http://127.0.0.1:8080",   # Localhost variants
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    # Lovable hackathon domains
    "https://app.lovable.dev",
    "https://preview.lovable.dev",
]
# Remove empty strings and duplicates
origins = list(set(o for o in origins if o))

# For hackathon/demo: allow all origins (restrict in production)
if settings.ENVIRONMENT == "development":
    allow_origins = origins
else:
    # Production: only allow specific origins
    allow_origins = origins if origins else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ──
# All routes centralized in app/api/router.py for cleaner main.py
app.include_router(router)


# ── Health Check ──
@app.get("/")
async def root():
    return {
        "service": "LaunchLens AI API",
        "status": "healthy",
        "version": "1.1.0",
        "description": "Complete startup market research & business planning platform",
        "core_endpoints": [
            "POST /api/decompose-idea",
            "POST /api/discover-insights",
            "POST /api/analyze-section",
            "POST /api/generate-setup",
            "POST /api/generate-validation",
        ],
        "new_features": [
            "POST /api/ideas - Save & manage research",
            "GET /api/ideas - List user's ideas",
            "GET /api/ideas/{id} - Retrieve idea",
            "PATCH /api/ideas/{id} - Update idea",
            "DELETE /api/ideas/{id} - Delete idea",
            "GET /api/ideas/{id}/export/pdf - Download PDF",
            "GET /api/ideas/{id}/progress - View module completion progress",
            "PATCH /api/ideas/{id}/progress - Update module progress status",
            "GET /api/ideas/{id}/analyses - View all cached analyses",
            "DELETE /api/ideas/{id}/analyses/{type} - Clear analysis cache",
        ],
        "analysis_endpoints": [
            "POST /api/analyze-risks - Risk Assessment (stores & caches)",
            "GET /api/ideas/{id}/risks - Retrieve cached risks",
            "POST /api/analyze-pricing - Pricing Strategy (stores & caches)",
            "GET /api/ideas/{id}/pricing - Retrieve cached pricing",
            "POST /api/analyze-financials - Financial Projections (stores & caches)",
            "GET /api/ideas/{id}/financials - Retrieve cached financials",
            "POST /api/analyze-customer-acquisition - Customer Acquisition (stores & caches)",
            "GET /api/ideas/{id}/acquisition - Retrieve cached acquisition",
        ],
        "docs": "http://localhost:8000/docs",
    }


@app.get("/health")
async def health():
    """Health check endpoint for Render uptime monitoring."""
    checks = {
        "groq_key": bool(settings.GROQ_API_KEY),
        "gemini_key": bool(settings.GEMINI_API_KEY),
        "serper_key": bool(settings.SERPER_API_KEY),
        "supabase_url": bool(settings.SUPABASE_URL),
    }
    return {
        "status": "healthy",
        "providers": checks,
        "environment": settings.ENVIRONMENT,
    }
