"""
Settings and configuration for LaunchLens.
Loads environment variables via Pydantic BaseSettings.
"""

import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Environment configuration from .env file."""

    # LLM Providers
    GROQ_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    HF_API_TOKEN: str = ""
    OPENROUTER_API_KEY: str = ""

    # Data Ingestion
    SERPER_API_KEY: str = ""
    TAVILY_API_KEY: str = ""

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    SUPABASE_JWT_SECRET: str = ""  # JWT signing secret for token verification

    # Reddit (optional, for authenticated scraping) - NOT CONFIGURED
    # REDDIT_CLIENT_ID: str = ""
    # REDDIT_CLIENT_SECRET: str = ""

    # App
    FRONTEND_URL: str = "http://localhost:3000"
    ENVIRONMENT: str = "development"  # Always use development mode for now (allows auth bypass)
    CORS_ORIGINS: str = ""  # Comma-separated list of allowed origins, empty = allow all

    # LLM Model Selection
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Create singleton settings instance
settings = get_settings()
