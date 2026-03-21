/**
 * Unified API layer for LaunchLens
 * Re-exports all API functionality for cleaner imports throughout the app
 */

// Core client and utilities
export { APIError, request } from './client';

// Research pipeline endpoints
export {
  decomposeIdea,
  discoverInsights,
  analyzeSection,
  generateSetup,
  generateValidation,
} from './research';

// Ideas management and advanced analysis
export {
  saveIdea,
  listIdeas,
  getIdea,
  updateIdea,
  deleteIdea,
  analyzeRisks,
  getRisks,
  analyzePricing,
  getPricing,
  analyzeFinancials,
  getFinancials,
  analyzeAcquisition,
  getAcquisition,
  type SaveIdeaRequest,
  type UpdateIdeaRequest,
  type IdeaResponse,
  type IdeaDetailResponse,
  type RiskAnalysisResponse,
  type PricingAnalysisResponse,
  type FinancialsAnalysisResponse,
  type AcquisitionAnalysisResponse,
} from './ideas';
