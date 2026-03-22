/**
 * Ideas management API endpoints
 * CRUD operations and advanced analysis caching
 * Uses Supabase JWT for authentication with the Render backend
 */

import { request } from './client';
import { supabase } from '@/lib/supabase';

/**
 * Authenticated request — injects Supabase JWT into Authorization header
 */
async function authRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const { data: { session } } = await supabase.auth.getSession();
  const token = session?.access_token;

  if (!token) {
    throw new Error('Not authenticated. Please sign in first.');
  }

  return request<T>(path, {
    ...options,
    headers: {
      ...(options.headers || {}),
      Authorization: `Bearer ${token}`,
    },
  });
}
/**
 * Idea data models (matching backend Pydantic schemas)
 */

export interface SaveIdeaRequest {
  title: string;
  description?: string;
  decomposition?: unknown;
  discover?: unknown;
  analyze?: unknown;
  setup?: unknown;
  validation?: unknown;
  tags?: string[];
  notes?: string;
}

export interface UpdateIdeaRequest {
  title?: string;
  description?: string;
  status?: string;
  decomposition?: unknown;
  discover?: unknown;
  analyze?: unknown;
  setup?: unknown;
  validation?: unknown;
  swot?: unknown;
  risks?: unknown;
  financials?: unknown;
  pricing?: unknown;
  acquisition?: unknown;
  tags?: string[];
  notes?: string;
}

export interface IdeaResponse {
  id: string;
  title: string;
  description?: string;
  status: string;
  created_at: string;
  updated_at: string;
  has_decompose: boolean;
  has_discover: boolean;
  has_analyze: boolean;
  has_setup: boolean;
  has_validate: boolean;
  tags: string[];
}

export interface IdeaDetailResponse {
  id: string;
  title: string;
  description?: string;
  status: string;
  decomposition?: unknown;
  discover?: unknown;
  analyze?: unknown;
  setup?: unknown;
  validation?: unknown;
  swot?: unknown;
  risks?: unknown;
  financials?: unknown;
  pricing?: unknown;
  acquisition?: unknown;
  tags: string[];
  notes?: string;
  created_at: string;
  updated_at: string;
}

/**
 * CRUD Operations
 */

/**
 * Save a new idea with research data
 */
export async function saveIdea(data: SaveIdeaRequest): Promise<IdeaResponse> {
  return authRequest<IdeaResponse>('/api/ideas', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * List user's saved ideas with optional filtering
 */
export async function listIdeas(
  status?: string,
  skip: number = 0,
  limit: number = 20,
): Promise<IdeaResponse[]> {
  const params = new URLSearchParams();
  if (status) params.append('status', status);
  params.append('skip', String(skip));
  params.append('limit', String(limit));

  return authRequest<IdeaResponse[]>(`/api/ideas?${params}`, {
    method: 'GET',
  });
}

/**
 * Get a specific idea with all its research data
 */
export async function getIdea(ideaId: string): Promise<IdeaDetailResponse> {
  return authRequest<IdeaDetailResponse>(`/api/ideas/${ideaId}`, {
    method: 'GET',
  });
}

/**
 * Update specific sections of an idea
 */
export async function updateIdea(ideaId: string, data: UpdateIdeaRequest): Promise<IdeaDetailResponse> {
  return authRequest<IdeaDetailResponse>(`/api/ideas/${ideaId}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

/**
 * Delete an idea
 */
export async function deleteIdea(ideaId: string): Promise<{ status: string; id: string; message: string }> {
  return authRequest<{ status: string; id: string; message: string }>(`/api/ideas/${ideaId}`, {
    method: 'DELETE',
  });
}

/**
 * Advanced Analysis Endpoints
 */

export interface RiskAnalysisResponse {
  id: string;
  idea_id: string;
  risks: unknown;
  created_at: string;
  updated_at: string;
}

export interface PricingAnalysisResponse {
  id: string;
  idea_id: string;
  pricing: unknown;
  created_at: string;
  updated_at: string;
}

export interface FinancialsAnalysisResponse {
  id: string;
  idea_id: string;
  financials: unknown;
  created_at: string;
  updated_at: string;
}

export interface AcquisitionAnalysisResponse {
  id: string;
  idea_id: string;
  acquisition: unknown;
  created_at: string;
  updated_at: string;
}

/**
 * Analyze risks for an idea (stores & caches)
 */
export async function analyzeRisks(
  ideaId: string,
  decomposition?: unknown,
  analysis_context?: unknown,
): Promise<RiskAnalysisResponse> {
  return authRequest<RiskAnalysisResponse>('/api/analyze-risks', {
    method: 'POST',
    body: JSON.stringify({ idea_id: ideaId, decomposition, analysis_context }),
  });
}

/**
 * Get cached risk analysis for an idea
 */
export async function getRisks(ideaId: string): Promise<RiskAnalysisResponse> {
  return authRequest<RiskAnalysisResponse>(`/api/ideas/${ideaId}/risks`, {
    method: 'GET',
  });
}

/**
 * Analyze pricing strategy (stores & caches)
 */
export async function analyzePricing(
  ideaId: string,
  decomposition?: unknown,
  analysis_context?: unknown,
): Promise<PricingAnalysisResponse> {
  return authRequest<PricingAnalysisResponse>('/api/analyze-pricing', {
    method: 'POST',
    body: JSON.stringify({ idea_id: ideaId, decomposition, analysis_context }),
  });
}

/**
 * Get cached pricing analysis for an idea
 */
export async function getPricing(ideaId: string): Promise<PricingAnalysisResponse> {
  return authRequest<PricingAnalysisResponse>(`/api/ideas/${ideaId}/pricing`, {
    method: 'GET',
  });
}

/**
 * Analyze financials and projections (stores & caches)
 */
export async function analyzeFinancials(
  ideaId: string,
  decomposition?: unknown,
  analysis_context?: unknown,
): Promise<FinancialsAnalysisResponse> {
  return authRequest<FinancialsAnalysisResponse>('/api/analyze-financials', {
    method: 'POST',
    body: JSON.stringify({ idea_id: ideaId, decomposition, analysis_context }),
  });
}

/**
 * Get cached financial analysis for an idea
 */
export async function getFinancials(ideaId: string): Promise<FinancialsAnalysisResponse> {
  return authRequest<FinancialsAnalysisResponse>(`/api/ideas/${ideaId}/financials`, {
    method: 'GET',
  });
}

/**
 * Analyze customer acquisition strategy (stores & caches)
 */
export async function analyzeAcquisition(
  ideaId: string,
  decomposition?: unknown,
  analysis_context?: unknown,
): Promise<AcquisitionAnalysisResponse> {
  return authRequest<AcquisitionAnalysisResponse>('/api/analyze-customer-acquisition', {
    method: 'POST',
    body: JSON.stringify({ idea_id: ideaId, decomposition, analysis_context }),
  });
}

/**
 * Get cached acquisition analysis for an idea
 */
export async function getAcquisition(ideaId: string): Promise<AcquisitionAnalysisResponse> {
  return authRequest<AcquisitionAnalysisResponse>(`/api/ideas/${ideaId}/acquisition`, {
    method: 'GET',
  });
}
