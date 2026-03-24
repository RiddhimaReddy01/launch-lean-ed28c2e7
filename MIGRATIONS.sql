-- Create research_cache table for storing all 5 tabs results
CREATE TABLE IF NOT EXISTS research_cache (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  idea_hash VARCHAR(255) NOT NULL,

  -- All 5 tabs cached as JSON
  decompose JSONB,
  discover JSONB,
  analyze JSONB,
  setup JSONB,
  validate JSONB,

  created_at TIMESTAMP DEFAULT NOW(),

  -- Index for fast lookups
  UNIQUE(user_id, idea_hash),
  FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE
);

-- Create index for faster cache lookups
CREATE INDEX idx_research_cache_user_idea ON research_cache(user_id, idea_hash);
CREATE INDEX idx_research_cache_created ON research_cache(created_at);

-- Auto-delete old cache entries (older than 7 days)
CREATE OR REPLACE FUNCTION delete_old_cache()
RETURNS void AS $$
BEGIN
  DELETE FROM research_cache WHERE created_at < NOW() - INTERVAL '7 days';
END;
$$ LANGUAGE plpgsql;
