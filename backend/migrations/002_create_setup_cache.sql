-- Create SETUP cache table for storing generated launch plans
CREATE TABLE IF NOT EXISTS setup_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    -- Format: "setup:{component}:{business_type}|{city}|{state}|{tier}"
    -- Example: "setup:suppliers:cold-pressed juice|San Francisco|CA|MID"

    data JSONB NOT NULL,  -- Full SetupResponse or component data

    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,  -- For TTL cleanup
    hit_count INT DEFAULT 0,  -- Analytics: how often cache was used

    CONSTRAINT cache_key_length CHECK (char_length(cache_key) <= 255)
);

-- Indexes for fast lookup
CREATE INDEX IF NOT EXISTS idx_setup_cache_key ON setup_cache(cache_key);
CREATE INDEX IF NOT EXISTS idx_setup_cache_expires ON setup_cache(expires_at);

-- Cleanup expired records automatically (optional, can also be done via background job)
-- Run periodically: DELETE FROM setup_cache WHERE expires_at < NOW();
