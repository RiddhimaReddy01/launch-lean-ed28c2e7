import { useQuery } from '@tanstack/react-query';
import { decomposeIdea, discoverInsights, analyzeSection, generateSetup, generateValidation } from '@/api';
import { useIdea } from '@/context/IdeaContext';
import type { AnalyzeResponse, SetupResponse, ValidateResponse } from '@/types/api';

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
  const { selectedInsight } = useIdea();

  return useQuery<AnalyzeResponse>({
    queryKey: ['analyze', section, idea, selectedInsight?.id],
    queryFn: () => analyzeSection(section, selectedInsight?.raw || selectedInsight, decomposeQuery.data),
    enabled: Boolean(idea && decomposeQuery.data && selectedInsight),
    staleTime: 1000 * 60 * 5,
  });
}

export function useSetupPlan(analysis_context?: Record<string, unknown>) {
  const { idea, decomposeQuery } = useResearchCore();
  const { selectedInsight } = useIdea();

  return useQuery<SetupResponse>({
    queryKey: ['setup', idea, selectedInsight?.id],
    queryFn: () => generateSetup(selectedInsight?.raw || selectedInsight, decomposeQuery.data, analysis_context),
    enabled: Boolean(idea && decomposeQuery.data && selectedInsight),
    staleTime: 1000 * 60 * 5,
  });
}

export function useValidationPlan(analysis_context?: Record<string, unknown>, setup_context?: Record<string, unknown>, channels?: string[]) {
  const { idea, decomposeQuery } = useResearchCore();
  const { selectedInsight } = useIdea();

  return useQuery<ValidateResponse>({
    queryKey: ['validate', idea, selectedInsight?.id, channels],
    queryFn: () => generateValidation(selectedInsight?.raw || selectedInsight, decomposeQuery.data, analysis_context, setup_context, channels),
    enabled: Boolean(idea && decomposeQuery.data && selectedInsight),
    staleTime: 1000 * 60 * 5,
  });
}
