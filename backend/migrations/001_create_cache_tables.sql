-- Migration: Create cache tables for decompose and discover
-- Enables persistent caching and multi-user benefit of cached results

-- Cache for decompose results (idea extraction)
CREATE TABLE IF NOT EXISTS decompose_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Query matching
    idea_hash VARCHAR(16) NOT NULL UNIQUE,
    idea TEXT NOT NULL,

    -- Cached decomposition result
    result JSONB NOT NULL,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '24 hours'),

    -- Index for fast lookups
    INDEX idx_decompose_hash (idea_hash),
    INDEX idx_decompose_expires (expires_at)
);

-- Cache for discover results (market insights)
CREATE TABLE IF NOT EXISTS discover_insights_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Cache key fields (for similarity matching)
    business_type TEXT NOT NULL,
    city TEXT,
    state VARCHAR(2),

    -- Cached discover results
    sources JSONB NOT NULL,
    insights JSONB NOT NULL,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '24 hours'),

    -- Unique constraint: only one cache entry per location + type combo
    UNIQUE(business_type, city, state),

    -- Indexes for fast lookups
    INDEX idx_discover_lookup (business_type, city, state),
    INDEX idx_discover_expires (expires_at)
);
