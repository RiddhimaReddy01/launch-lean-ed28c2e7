-- Create idea_insights table for saving insights per idea
-- Stores individual insights extracted from ANALYZE section analysis

CREATE TABLE IF NOT EXISTS public.idea_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    idea_id UUID NOT NULL REFERENCES public.ideas(id) ON DELETE CASCADE,
    section TEXT NOT NULL DEFAULT 'opportunity',  -- opportunity | customers | competitors | rootcause | costs | risk | location | moat
    title TEXT NOT NULL,
    content JSONB NOT NULL,  -- Full insight content
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],  -- Array of tags for filtering
    pinned BOOLEAN DEFAULT FALSE,  -- User can pin important insights
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Create indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_idea_insights_user_id ON public.idea_insights(user_id);
CREATE INDEX IF NOT EXISTS idx_idea_insights_idea_id ON public.idea_insights(idea_id);
CREATE INDEX IF NOT EXISTS idx_idea_insights_section ON public.idea_insights(section);
CREATE INDEX IF NOT EXISTS idx_idea_insights_pinned ON public.idea_insights(pinned);

-- Enable RLS (Row Level Security)
ALTER TABLE public.idea_insights ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
-- Users can only view their own insights
CREATE POLICY IF NOT EXISTS "Users can view own insights"
    ON public.idea_insights
    FOR SELECT
    USING (auth.uid() = user_id);

-- Users can only insert their own insights
CREATE POLICY IF NOT EXISTS "Users can insert own insights"
    ON public.idea_insights
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can only update their own insights
CREATE POLICY IF NOT EXISTS "Users can update own insights"
    ON public.idea_insights
    FOR UPDATE
    USING (auth.uid() = user_id);

-- Users can only delete their own insights
CREATE POLICY IF NOT EXISTS "Users can delete own insights"
    ON public.idea_insights
    FOR DELETE
    USING (auth.uid() = user_id);

-- Create profiles table if it doesn't exist (for profile management)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    display_name TEXT,
    avatar_url TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Enable RLS for profiles
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for profiles
CREATE POLICY IF NOT EXISTS "Users can view own profile"
    ON public.profiles
    FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY IF NOT EXISTS "Users can update own profile"
    ON public.profiles
    FOR UPDATE
    USING (auth.uid() = id);

CREATE POLICY IF NOT EXISTS "Users can insert own profile"
    ON public.profiles
    FOR INSERT
    WITH CHECK (auth.uid() = id);
