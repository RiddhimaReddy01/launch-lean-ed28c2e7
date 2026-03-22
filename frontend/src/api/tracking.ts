/**
 * Validation tracking API endpoints
 * Save and fetch validation experiment metrics to/from database
 */

import { request } from './client';

export interface ValidationExperiment {
  id: string;
  idea_id: string;
  methods: string[];
  waitlist_signups: number;
  survey_completions: number;
  would_switch_rate: number;
  price_tolerance_avg: number;
  community_engagement: number;
  reddit_upvotes: number;
  // Revenue validation
  paid_signups: number;
  revenue_collected: number;
  ad_spend: number;
  // Calculated economics
  cac: number | null;
  ltv_cac_ratio: number | null;
  verdict: string | null;
  reasoning: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface CreateValidationExperimentRequest {
  idea_id: string;
  methods: string[];
  metrics: {
    waitlist_signups: number;
    survey_completions: number;
    would_switch_rate: number;
    price_tolerance_avg: number;
    community_engagement: number;
    reddit_upvotes: number;
    // Revenue validation
    paid_signups?: number;
    revenue_collected?: number;
    ad_spend?: number;
  };
}

/**
 * Create a new validation experiment
 */
export async function createValidationExperiment(
  req: CreateValidationExperimentRequest,
): Promise<ValidationExperiment> {
  return request<ValidationExperiment>('/api/validation-experiments', {
    method: 'POST',
    body: JSON.stringify(req),
  });
}

/**
 * Fetch all validation experiments for an idea
 */
export async function getValidationExperiments(
  ideaId: string,
): Promise<{ experiments: ValidationExperiment[]; count: number }> {
  return request<{ experiments: ValidationExperiment[]; count: number }>(
    `/api/validation-experiments/${ideaId}`,
    { method: 'GET' },
  );
}

/**
 * Update validation experiment metrics
 */
export async function updateValidationExperiment(
  experimentId: string,
  metrics: Partial<{
    waitlist_signups: number;
    survey_completions: number;
    would_switch_rate: number;
    price_tolerance_avg: number;
    community_engagement: number;
    reddit_upvotes: number;
    paid_signups: number;
    revenue_collected: number;
    ad_spend: number;
  }>,
): Promise<ValidationExperiment> {
  return request<ValidationExperiment>(
    `/api/validation-experiments/${experimentId}`,
    {
      method: 'PATCH',
      body: JSON.stringify(metrics),
    },
  );
}
