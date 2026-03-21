-- SEED_SAMPLE_DATA.sql
-- Run this in your Supabase SQL Editor AFTER running SETUP_DATABASE.sql
-- It requires at least one user to exist in the auth.users table.
-- Automatically grabs the first user in the system to assign these samples to.

DO $$
DECLARE
  v_user_id UUID;
  v_idea1_id UUID := gen_random_uuid();
  v_idea2_id UUID := gen_random_uuid();
  v_idea3_id UUID := gen_random_uuid();
BEGIN
  -- 1. Get a user ID to attach the samples to
  SELECT id INTO v_user_id FROM auth.users LIMIT 1;

  IF v_user_id IS NULL THEN
    RAISE NOTICE 'No user found in auth.users. Please sign up at least one user via the frontend before running this script.';
    RETURN;
  END IF;

  -- 2. Insert 3 Realistic Sample Ideas
  
  -- Idea 1: AI Tutoring Service (Strong GO)
  INSERT INTO public.ideas (id, user_id, title, status, decomposition, discover, created_at, updated_at)
  VALUES (
    v_idea1_id,
    v_user_id,
    'AI SAT Tutoring for High Schoolers in Frisco TX',
    'completed',
    '{"business_type": "Education Technology", "location": {"city": "Frisco", "state": "TX"}, "target_customers": ["High school students", "Parents"], "price_tier": "Premium", "search_queries": ["SAT tutors Frisco TX", "average cost of SAT prep Frisco", "parents complaints about SAT tutoring"]}'::jsonb,
    '{"insights": [{"id": "ins_001", "type": "pain_point", "score": 9.2, "title": "Traditional SAT prep is too expensive ($150+/hr)", "evidence": [{"date": "2024-01-15", "quote": "I am paying $200 an hour and my son still is struggling with the math section.", "score": 9, "source": "Frisco Moms Group"}], "frequency_score": 8, "intensity_score": 9, "mention_count": 142, "source_ids": ["google", "reddit"], "willingness_to_pay_score": 8}], "sources": [{"id": "google", "name": "Google Search", "type": "search", "post_count": 8, "url": "#", "active": false}]}'::jsonb,
    now() - interval '2 days',
    now() - interval '2 days'
  );

  -- Idea 2: Local Plant Nursery (PIVOT)
  INSERT INTO public.ideas (id, user_id, title, status, decomposition, discover, created_at, updated_at)
  VALUES (
    v_idea2_id,
    v_user_id,
    'Exotic Indoor Plant Nursery in Austin TX',
    'completed',
    '{"business_type": "Retail Nursery", "location": {"city": "Austin", "state": "TX"}, "target_customers": ["Millennials", "Apartment Dwellers"]}'::jsonb,
    '{"insights": [{"id": "ins_002", "type": "unmet_want", "score": 7.5, "title": "Want rare aroids but shipping is stressful", "evidence": [{"date": "2024-02-10", "quote": "My Thai Constellation arrived with root rot from Etsy.", "score": 8, "source": "r/RareHouseplants"}], "frequency_score": 6, "intensity_score": 8, "mention_count": 85, "source_ids": ["reddit"], "willingness_to_pay_score": 9}]}'::jsonb,
    now() - interval '5 days',
    now() - interval '5 days'
  );

  -- Idea 3: Mobile Pet Grooming (KILL)
  INSERT INTO public.ideas (id, user_id, title, status, decomposition, discover, created_at, updated_at)
  VALUES (
    v_idea3_id,
    v_user_id,
    'Mobile Pet Grooming with Organic Products in Seattle',
    'completed',
    '{"business_type": "Pet Services", "location": {"city": "Seattle", "state": "WA"}, "target_customers": ["Dog owners", "Eco-conscious consumers"]}'::jsonb,
    '{"insights": [{"id": "ins_003", "type": "market_gap", "score": 4.1, "title": "Market is super saturated with mobile groomers", "evidence": [{"date": "2024-03-01", "quote": "There are 4 mobile groomers on my street alone.", "score": 4, "source": "Nextdoor"}], "frequency_score": 9, "intensity_score": 3, "mention_count": 210, "source_ids": ["google"], "willingness_to_pay_score": 4}]}'::jsonb,
    now() - interval '10 days',
    now() - interval '10 days'
  );

  -- 3. Insert specific Validation Experiments for these ideas
  
  -- Experiment for Idea 1 (GO - Strong Metrics)
  INSERT INTO public.validation_experiments (id, user_id, idea_id, methods, waitlist_signups, survey_completions, would_switch_rate, price_tolerance_avg, verdict, reasoning, created_at, updated_at)
  VALUES (
    gen_random_uuid(), v_user_id, v_idea1_id,
    ARRAY['landing', 'survey', 'social'],
    185, 92, 75, 59.00,
    'go',
    'Strong demand signal with healthy price tolerance. High volume of signups indicates parents are actively looking for alternatives to expensive SAT prep. Move forward with confidence.',
    now() - interval '1 day',
    now() - interval '1 day'
  );

  -- Experiment for Idea 2 (PIVOT - Mixed Signals)
  INSERT INTO public.validation_experiments (id, user_id, idea_id, methods, waitlist_signups, survey_completions, would_switch_rate, price_tolerance_avg, verdict, reasoning, created_at, updated_at)
  VALUES (
    gen_random_uuid(), v_user_id, v_idea2_id,
    ARRAY['landing', 'marketplace'],
    95, 30, 45, 120.00,
    'pivot',
    'Strong interest but low conversion probability—consider repositioning. Customers want the product but hesitate due to high price points or operational constraints.',
    now() - interval '4 days',
    now() - interval '4 days'
  );

  -- Experiment for Idea 3 (KILL - Poor Metrics)
  INSERT INTO public.validation_experiments (id, user_id, idea_id, methods, waitlist_signups, survey_completions, would_switch_rate, price_tolerance_avg, verdict, reasoning, created_at, updated_at)
  VALUES (
    gen_random_uuid(), v_user_id, v_idea3_id,
    ARRAY['direct', 'social'],
    12, 18, 15, 65.00,
    'kill',
    'Low interest across channels. The market saturation makes acquisition costs extremely high. Consider a fundamentally different value proposition.',
    now() - interval '9 days',
    now() - interval '9 days'
  );

  RAISE NOTICE 'Successfully seeded 3 sample ideas and experiments for user: %', v_user_id;
END $$;
