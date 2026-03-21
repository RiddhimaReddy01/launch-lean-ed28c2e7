/**
 * Research pipeline API endpoints
 * Core functions: Decompose, Discover, Analyze, Setup, Validate
 */

import type { DecomposeResponse, DiscoverResponse, AnalyzeResponse, SetupResponse, ValidateResponse } from '@/types/api';
import { request } from './client';

/**
 * Decompose an idea into structured components
 */
export async function decomposeIdea(idea: string): Promise<DecomposeResponse> {
  return request<DecomposeResponse>('/api/decompose-idea', {
    method: 'POST',
    body: JSON.stringify({ idea }),
  });
}

/**
 * Discover insights based on idea decomposition
 */
export async function discoverInsights(decomposition: unknown): Promise<DiscoverResponse> {
  return request<DiscoverResponse>('/api/discover-insights', {
    method: 'POST',
    body: JSON.stringify({ decomposition }),
  });
}

/**
 * Analyze a specific section with insights and context
 */
export async function analyzeSection(
  section: string,
  insight: unknown,
  decomposition: unknown,
  prior_context?: unknown,
): Promise<AnalyzeResponse> {
  return request<AnalyzeResponse>('/api/analyze-section', {
    method: 'POST',
    body: JSON.stringify({ section, insight, decomposition, prior_context }),
  });
}

/**
 * Generate setup/validation recommendations
 */
export async function generateSetup(
  insight: unknown,
  decomposition: unknown,
  analysis_context?: unknown,
): Promise<SetupResponse> {
  return request<SetupResponse>('/api/generate-setup', {
    method: 'POST',
    body: JSON.stringify({ insight, decomposition, analysis_context }),
  });
}

/**
 * Generate validation strategy and metrics
 */
export async function generateValidation(
  insight: unknown,
  decomposition: unknown,
  analysis_context?: unknown,
  setup_context?: unknown,
  channels?: string[],
): Promise<ValidateResponse> {
  return request<ValidateResponse>('/api/generate-validation', {
    method: 'POST',
    body: JSON.stringify({
      insight,
      decomposition,
      analysis_context,
      setup_context,
      channels: channels || ['landing_page', 'survey'],
    }),
  });
}
