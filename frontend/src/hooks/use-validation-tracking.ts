import { useState, useCallback } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import {
  createValidationExperiment,
  getValidationExperiments,
  updateValidationExperiment,
  type ValidationExperiment,
  type CreateValidationExperimentRequest,
} from '@/api';
import { useIdea } from '@/context/IdeaContext';

/**
 * Hook for managing validation experiment tracking
 */
export function useValidationTracking() {
  const { idea } = useIdea();
  const [currentExperiment, setCurrentExperiment] = useState<ValidationExperiment | null>(null);

  // Fetch all experiments for the current idea
  const experimentsQuery = useQuery({
    queryKey: ['validation-experiments', idea],
    queryFn: () => getValidationExperiments(idea),
    enabled: Boolean(idea),
    staleTime: 1000 * 60 * 5,
  });

  // Create new experiment
  const createMutation = useMutation({
    mutationFn: (req: CreateValidationExperimentRequest) => createValidationExperiment(req),
    onSuccess: (data) => {
      setCurrentExperiment(data);
      // Refetch experiments list
      experimentsQuery.refetch();
    },
  });

  // Update experiment metrics
  const updateMutation = useMutation({
    mutationFn: ({
      experimentId,
      metrics,
    }: {
      experimentId: string;
      metrics: Parameters<typeof updateValidationExperiment>[1];
    }) => updateValidationExperiment(experimentId, metrics),
    onSuccess: (data) => {
      setCurrentExperiment(data);
      // Refetch experiments list
      experimentsQuery.refetch();
    },
  });

  const saveExperiment = useCallback(
    async (
      ideaId: string,
      methods: string[],
      metrics: {
        waitlist_signups: number;
        survey_completions: number;
        would_switch_rate: number;
        price_tolerance_avg: number;
        community_engagement: number;
        reddit_upvotes: number;
        paid_signups?: number;
        revenue_collected?: number;
        ad_spend?: number;
      },
    ) => {
      return createMutation.mutateAsync({
        idea_id: ideaId,
        methods,
        metrics,
      });
    },
    [createMutation],
  );

  const updateMetrics = useCallback(
    async (
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
    ) => {
      return updateMutation.mutateAsync({
        experimentId,
        metrics,
      });
    },
    [updateMutation],
  );

  return {
    experiments: experimentsQuery.data?.experiments || [],
    experimentsCount: experimentsQuery.data?.count || 0,
    currentExperiment,
    saveExperiment,
    updateMetrics,
    isLoading: experimentsQuery.isLoading || createMutation.isPending || updateMutation.isPending,
    isError: experimentsQuery.isError || createMutation.isError || updateMutation.isError,
    error: experimentsQuery.error || createMutation.error || updateMutation.error,
  };
}
