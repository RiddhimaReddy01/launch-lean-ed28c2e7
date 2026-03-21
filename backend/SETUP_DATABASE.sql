-- LaunchLens Database Schema Setup
-- Run this in Supabase SQL Editor
-- Go to: https://app.supabase.com → Your Project → SQL Editor
-- Paste all of this and click "Run"

-- ═══════════════════════════════════════════════════════════════
-- MAIN IDEAS TABLE - Stores all user research
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE ideas (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

  -- Basic metadata
  title VARCHAR(255) NOT NULL,
  description TEXT,
  status VARCHAR(50) DEFAULT 'draft',  -- draft, in_progress, completed, archived

  -- All research data stored as JSON
  decomposition JSONB,           -- Output from /api/decompose-idea
  discover JSONB,                -- Output from /api/discover-insights
  "analyze" JSONB,               -- All 5 analyze sections + new ones
  setup JSONB,                   -- Output from /api/generate-setup
  validate JSONB,                -- Output from /api/generate-validation

  -- New features
  swot JSONB,                    -- Output from /api/analyze-swot
  risks JSONB,                   -- Output from /api/analyze-risks
  financials JSONB,              -- Output from /api/analyze-financials
  pricing JSONB,                 -- Output from /api/analyze-pricing
  acquisition JSONB,             -- Output from /api/analyze-customer-acquisition

  -- Module Progress Tracking (like the plan phases)
  decompose_status VARCHAR(20) DEFAULT 'pending',     -- pending, in_progress, completed
  decompose_completed_at TIMESTAMP,
  discover_status VARCHAR(20) DEFAULT 'pending',
  discover_completed_at TIMESTAMP,
  analyze_status VARCHAR(20) DEFAULT 'pending',
  analyze_completed_at TIMESTAMP,
  setup_status VARCHAR(20) DEFAULT 'pending',
  setup_completed_at TIMESTAMP,
  validate_status VARCHAR(20) DEFAULT 'pending',
  validate_completed_at TIMESTAMP,

  -- Analysis Result Timestamps & Assumptions (for caching)
  risks_calculated_at TIMESTAMP,
  risks_assumptions JSONB,                  -- Store the assumptions used (CAC rate, churn, etc.)

  pricing_calculated_at TIMESTAMP,
  pricing_assumptions JSONB,

  financials_calculated_at TIMESTAMP,
  financials_assumptions JSONB DEFAULT '{"customer_acquisition_rate": 3, "average_revenue_per_customer": 150, "churn_rate": 0.05, "growth_rate": 0.02}'::jsonb,

  acquisition_calculated_at TIMESTAMP,
  acquisition_assumptions JSONB,

  -- Tags for organization
  tags TEXT[] DEFAULT '{}',
  notes TEXT,

  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),

  -- Unique constraint: one title per user
  UNIQUE(user_id, title)
);

-- ═══════════════════════════════════════════════════════════════
-- INDEXES for faster queries
-- ═══════════════════════════════════════════════════════════════

CREATE INDEX ideas_user_id_idx ON ideas(user_id);
CREATE INDEX ideas_status_idx ON ideas(status);
CREATE INDEX ideas_created_at_idx ON ideas(created_at DESC);
CREATE INDEX ideas_updated_at_idx ON ideas(updated_at DESC);

-- ═══════════════════════════════════════════════════════════════
-- ENABLE ROW LEVEL SECURITY
-- ═══════════════════════════════════════════════════════════════

ALTER TABLE ideas ENABLE ROW LEVEL SECURITY;

-- Users can only see their own ideas
CREATE POLICY "Users can view their own ideas"
  ON ideas
  FOR SELECT
  USING (auth.uid() = user_id);

-- Users can insert their own ideas
CREATE POLICY "Users can insert their own ideas"
  ON ideas
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Users can update their own ideas
CREATE POLICY "Users can update their own ideas"
  ON ideas
  FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- Users can delete their own ideas
CREATE POLICY "Users can delete their own ideas"
  ON ideas
  FOR DELETE
  USING (auth.uid() = user_id);

-- ═══════════════════════════════════════════════════════════════
-- AUTO UPDATE TIMESTAMP TRIGGER
-- ═══════════════════════════════════════════════════════════════

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_ideas_updated_at
  BEFORE UPDATE ON ideas
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- ═══════════════════════════════════════════════════════════════
-- VALIDATION EXPERIMENTS TABLE - Tracks validation metrics over time
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE validation_experiments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  idea_id UUID NOT NULL REFERENCES ideas(id) ON DELETE CASCADE,

  -- Method selections (array of method IDs)
  methods TEXT[] DEFAULT '{}',

  -- Experiment metrics
  waitlist_signups INT DEFAULT 0,
  survey_completions INT DEFAULT 0,
  would_switch_rate FLOAT DEFAULT 0,
  price_tolerance_avg FLOAT DEFAULT 0,
  community_engagement INT DEFAULT 0,
  reddit_upvotes INT DEFAULT 0,

  -- Verdict and reasoning
  verdict VARCHAR(20),  -- go, pivot, kill, awaiting
  reasoning TEXT,

  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for faster queries
CREATE INDEX validation_experiments_user_id_idx ON validation_experiments(user_id);
CREATE INDEX validation_experiments_idea_id_idx ON validation_experiments(idea_id);
CREATE INDEX validation_experiments_created_at_idx ON validation_experiments(created_at DESC);

-- Enable RLS
ALTER TABLE validation_experiments ENABLE ROW LEVEL SECURITY;

-- Users can only see their own validation experiments
CREATE POLICY "Users can view their own validation experiments"
  ON validation_experiments
  FOR SELECT
  USING (auth.uid() = user_id);

-- Users can insert their own validation experiments
CREATE POLICY "Users can insert their own validation experiments"
  ON validation_experiments
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Users can update their own validation experiments
CREATE POLICY "Users can update their own validation experiments"
  ON validation_experiments
  FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- Users can delete their own validation experiments
CREATE POLICY "Users can delete their own validation experiments"
  ON validation_experiments
  FOR DELETE
  USING (auth.uid() = user_id);

-- Auto-update timestamp
CREATE TRIGGER update_validation_experiments_updated_at
  BEFORE UPDATE ON validation_experiments
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- ═══════════════════════════════════════════════════════════════
-- DONE!
-- ═══════════════════════════════════════════════════════════════
-- You can now:
-- 1. Check Supabase → Database → Tables → Should see "ideas" and "validation_experiments"
-- 2. Check Supabase → Authentication → Users (for auth.users reference)
-- 3. Now run the Python backend code
