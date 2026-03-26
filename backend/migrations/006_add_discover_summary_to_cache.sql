-- Migration: add summary payload to discover cache
-- Purpose: persist Discover summary metrics such as demand strength and mixed signals

ALTER TABLE IF EXISTS discover_insights_cache
ADD COLUMN IF NOT EXISTS summary JSONB NOT NULL DEFAULT '{}'::jsonb;

