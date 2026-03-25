-- Migration: Create search_results_cache table
-- Purpose: Persist Google/Serper/Tavily query results so repeated demo traffic
-- can reuse search outputs instead of re-fetching external sources.

CREATE TABLE IF NOT EXISTS search_results_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_hash VARCHAR(16) NOT NULL UNIQUE,
    results JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '7 days')
);

CREATE INDEX IF NOT EXISTS idx_search_results_query_hash
    ON search_results_cache (query_hash);

CREATE INDEX IF NOT EXISTS idx_search_results_expires_at
    ON search_results_cache (expires_at);
