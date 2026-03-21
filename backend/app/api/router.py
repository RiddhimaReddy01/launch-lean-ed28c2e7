"""
Central router registration for all LaunchLens API endpoints.
This keeps main.py clean by consolidating all include_router calls.
"""

from fastapi import APIRouter

from app.api import (
    decompose,
    discover,
    analyze,
    analysis,
    setup,
    validate,
    ideas,
    export,
    progress,
)

# Create main router
router = APIRouter()

# Core research pipeline (5 main endpoints)
router.include_router(decompose.router, tags=["Decompose"])
router.include_router(discover.router, tags=["Discover"])
router.include_router(analyze.router, tags=["Analyze"])
router.include_router(setup.router, tags=["Setup"])
router.include_router(validate.router, tags=["Validate"])

# New features
router.include_router(ideas.router, tags=["Ideas"])
router.include_router(export.router, tags=["Export"])
router.include_router(analysis.router, tags=["Advanced Analysis"])
router.include_router(progress.router, tags=["Progress Tracking"])
