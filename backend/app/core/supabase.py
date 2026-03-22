"""
Centralized Supabase client factory for database access.
Provides a single source of truth for Supabase connection management.
"""

import logging
from supabase import create_client

from app.core.config import settings

logger = logging.getLogger(__name__)


def get_supabase():
    """
    Get Supabase client instance.
    Initializes with SUPABASE_URL and SUPABASE_SERVICE_KEY from config.
    """
    try:
        return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {e}")
        raise
