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
APP_VERSION = "1.1.0"
app = FastAPI(
    title="LaunchLens AI API",
    description="Backend API for LaunchLens AI - startup market research platform",
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──
# Allow all origins for Cloudflare Tunnel + Lovable
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600,
)

# ── Startup Validation ──
@app.on_event("startup")
async def validate_environment():
    """Validate required environment variables at startup."""
    required_vars = {
        "GROQ_API_KEY": settings.GROQ_API_KEY,
        "SERPER_API_KEY": settings.SERPER_API_KEY,
        "SUPABASE_URL": settings.SUPABASE_URL,
        "SUPABASE_SERVICE_KEY": settings.SUPABASE_SERVICE_KEY,
        "SUPABASE_JWT_SECRET": settings.SUPABASE_JWT_SECRET,
    }

    missing = [name for name, value in required_vars.items() if not value]
    if missing:
        logger.error(f"❌ Missing required environment variables: {', '.join(missing)}")
        raise RuntimeError(f"Cannot start: missing {len(missing)} required env vars. Set these before startup.")

    logger.info("✅ All required environment variables configured")

# ── Routes ──
# All routes centralized in app/api/router.py for cleaner main.py
app.include_router(router)


# ── Debug Endpoint ──
@app.get("/debug/llm-test")
async def test_llm():
    """Debug endpoint to test LLM connectivity"""
    from app.services.llm_client import call_llm
    import traceback

    try:
        result = await call_llm(
            system_prompt="You are helpful",
            user_prompt="Say hello in JSON: {\"greeting\": \"...\"}",
            max_tokens=50,
            json_mode=True
        )
        return {
            "status": "SUCCESS",
            "result": result,
            "message": "LLM working!"
        }
    except Exception as e:
        logger.error(f"LLM Error: {e}\n{traceback.format_exc()}")
        return {
            "status": "ERROR",
            "error_type": type(e).__name__,
            "error_message": str(e),
            "traceback": traceback.format_exc()
        }


# ── Health Check ──
@app.get("/")
async def root():
    return {
        "service": "LaunchLens AI API",
        "status": "healthy",
        "version": APP_VERSION,
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
        "docs": "/docs",  # Available at the service URL
    }


@app.get("/health")
async def health():
    """Health check endpoint for Render uptime monitoring."""
    from app.core.supabase import get_supabase

    checks = {
        "groq_key": bool(settings.GROQ_API_KEY),
        "gemini_key": bool(settings.GEMINI_API_KEY),
        "serper_key": bool(settings.SERPER_API_KEY),
        "supabase_url": bool(settings.SUPABASE_URL),
        "database": False,
    }

    # Check database connectivity
    try:
        supabase = get_supabase()
        # Simple query to verify connection
        supabase.table("ideas").select("id").limit(1).execute()
        checks["database"] = True
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")
        checks["database"] = False

    status = "healthy" if all(checks.values()) else "degraded"
    return {
        "status": status,
        "providers": checks,
        "environment": settings.ENVIRONMENT,
    }


# ── Exception Handlers ──
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Catch unhandled exceptions and return proper error response."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=exc)
    return {
        "status": "error",
        "message": "Internal server error",
        "detail": str(exc) if settings.ENVIRONMENT == "development" else None,
    }
