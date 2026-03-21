/**
 * Centralized type exports for the entire application
 * Import all types from here instead of scattered locations
 */

// API response types
export type {
  DecomposeResponse,
  DiscoverEvidence,
  DiscoverInsight,
  DiscoverSource,
  DiscoverResponse,
  AnalyzeResponse,
  SetupResponse,
  ValidateResponse,
} from './api';

// Domain types
export type { Step } from '../context/IdeaContext';

// Re-export data types for backward compatibility
export type { Insight, Source, Evidence } from '../test/__mocks__/discover';
