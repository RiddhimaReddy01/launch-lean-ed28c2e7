"""
Centralized Supabase client singleton.
Reuses a single client instance to avoid creating new HTTP connection
pools on every call (each create_client allocates ~5-10 MB).
"""

import logging
from supabase import create_client

from app.core.config import settings

logger = logging.getLogger(__name__)

_client = None


def get_supabase():
    """Return the shared Supabase client, creating it once on first use."""
    global _client
    if _client is None:
        try:
            _client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
        except Exception as e:
            logger.error(f"Failed to create Supabase client: {e}")
            raise
    return _client
