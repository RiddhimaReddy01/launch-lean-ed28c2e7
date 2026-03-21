import { useQuery } from '@tanstack/react-query';
import { decomposeIdea, discoverInsights, analyzeSection, generateSetup, generateValidation } from '@/api';
import { useIdea } from '@/context/IdeaContext';
import type { AnalyzeResponse, SetupResponse, ValidateResponse } from '@/types/api';
import { useEffect } from 'react';

export function useResearchCore() {
  const { idea } = useIdea();

  const decomposeQuery = useQuery({
    queryKey: ['decompose', idea],
    queryFn: () => decomposeIdea(idea),
    enabled: Boolean(idea),
    staleTime: 1000 * 60 * 5,
  });

  const discoverQuery = useQuery({
    queryKey: ['discover', idea],
    queryFn: () => discoverInsights(decomposeQuery.data!),
    enabled: Boolean(idea) && Boolean(decomposeQuery.data),
    staleTime: 1000 * 60 * 5,
  });

  return { idea, decomposeQuery, discoverQuery };
}

export function useAnalyzeSection(section: string) {
  const { idea, decomposeQuery } = useResearchCore();
  const { selectedInsight, storeAnalysis, pipeline } = useIdea();

  const query = useQuery<AnalyzeResponse>({
    queryKey: ['analyze', section, idea, selectedInsight?.id],
    queryFn: () =>
      analyzeSection(
        section,
        selectedInsight?.raw || selectedInsight,
        decomposeQuery.data,
        Object.keys(pipeline.analysisContext).length > 0 ? pipeline.analysisContext : undefined,
      ),
    enabled: Boolean(idea && decomposeQuery.data && selectedInsight),
    staleTime: 1000 * 60 * 5,
  });

  // Store results in pipeline context when they arrive
  useEffect(() => {
    if (query.data) {
      storeAnalysis(section, query.data.data);
    }
  }, [query.data, section, storeAnalysis]);

  return query;
}

export function useSetupPlan() {
  const { idea, decomposeQuery } = useResearchCore();
  const { selectedInsight, storeSetup, pipeline } = useIdea();

  const analysisCtx = Object.keys(pipeline.analysisContext).length > 0
    ? pipeline.analysisContext
    : undefined;

  const query = useQuery<SetupResponse>({
    queryKey: ['setup', idea, selectedInsight?.id],
    queryFn: () =>
      generateSetup(
        selectedInsight?.raw || selectedInsight,
        decomposeQuery.data,
        analysisCtx,
      ),
    enabled: Boolean(idea && decomposeQuery.data && selectedInsight),
    staleTime: 1000 * 60 * 5,
  });

  // Store results for validate module
  useEffect(() => {
    if (query.data) {
      storeSetup(query.data as unknown as Record<string, unknown>);
    }
  }, [query.data, storeSetup]);

  return query;
}

export function useValidationPlan() {
  const { idea, decomposeQuery } = useResearchCore();
  const { selectedInsight, pipeline } = useIdea();

  const analysisCtx = Object.keys(pipeline.analysisContext).length > 0
    ? pipeline.analysisContext
    : undefined;

  return useQuery<ValidateResponse>({
    queryKey: ['validate', idea, selectedInsight?.id],
    queryFn: () =>
      generateValidation(
        selectedInsight?.raw || selectedInsight,
        decomposeQuery.data,
        analysisCtx,
        pipeline.setupContext || undefined,
      ),
    enabled: Boolean(idea && decomposeQuery.data && selectedInsight),
    staleTime: 1000 * 60 * 5,
  });
}
