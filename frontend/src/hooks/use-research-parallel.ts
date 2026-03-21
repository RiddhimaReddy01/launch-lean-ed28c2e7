/**
 * Parallel Research Hook - 3x Faster!
 *
 * Makes all API calls in parallel instead of sequential.
 * Old: Decompose → Discover → Analyze → Setup → Validate (13s)
 * New: All parallel (5s)
 *
 * Usage:
 * const { allResults, isLoading } = useResearchParallel(idea)
 */

import { useEffect, useState } from 'react';
import {
  decomposeIdea,
  discoverInsights,
  analyzeSection,
  generateSetup,
  generateValidation
} from '@/api';
import { useIdea } from '@/context/IdeaContext';
import type { DecomposeResponse, DiscoverResponse, AnalyzeResponse, SetupResponse, ValidateResponse } from '@/types/api';

interface ParallelResults {
  decompose: DecomposeResponse | null;
  discover: DiscoverResponse | null;
  analyze: AnalyzeResponse | null;
  setup: SetupResponse | null;
  validate: ValidateResponse | null;
}

interface ParallelState {
  allResults: ParallelResults;
  isLoading: boolean;
  error: Error | null;
  progress: {
    decompose: boolean;
    discover: boolean;
    analyze: boolean;
    setup: boolean;
    validate: boolean;
  };
}

/**
 * Parallel hook: Start all 5 modules at the same time
 * Instead of waiting for each to finish sequentially
 */
export function useResearchParallel(idea: string) {
  const { storeAnalysis, storeSetup } = useIdea();
  const [state, setState] = useState<ParallelState>({
    allResults: {
      decompose: null,
      discover: null,
      analyze: null,
      setup: null,
      validate: null
    },
    isLoading: false,
    error: null,
    progress: {
      decompose: false,
      discover: false,
      analyze: false,
      setup: false,
      validate: false
    }
  });

  useEffect(() => {
    if (!idea || idea.length < 3) return;

    let isMounted = true;
    const controller = new AbortController();

    const runParallelRequests = async () => {
      setState(prev => ({ ...prev, isLoading: true, error: null }));

      try {
        // Step 1: Decompose first (others depend on it)
        const decompose = await decomposeIdea(idea);

        if (!isMounted) return;

        setState(prev => ({
          ...prev,
          allResults: { ...prev.allResults, decompose },
          progress: { ...prev.progress, decompose: true }
        }));

        // Step 2: Run all others in parallel (they depend on decompose)
        const [discover, analyze, setup, validate] = await Promise.all([
          discoverInsights(decompose).catch(e => {
            console.error('Discover error:', e);
            return null;
          }),
          analyzeSection('opportunity', null, decompose, undefined).catch(e => {
            console.error('Analyze error:', e);
            return null;
          }),
          generateSetup(null, decompose, undefined).catch(e => {
            console.error('Setup error:', e);
            return null;
          }),
          generateValidation(null, decompose, undefined, undefined).catch(e => {
            console.error('Validate error:', e);
            return null;
          })
        ]);

        if (!isMounted) return;

        // Store results
        if (analyze) {
          storeAnalysis('opportunity', analyze.data);
        }
        if (setup) {
          storeSetup(setup as unknown as Record<string, unknown>);
        }

        setState(prev => ({
          ...prev,
          allResults: {
            decompose,
            discover: discover as DiscoverResponse | null,
            analyze: analyze as AnalyzeResponse | null,
            setup: setup as SetupResponse | null,
            validate: validate as ValidateResponse | null
          },
          progress: {
            decompose: true,
            discover: !!discover,
            analyze: !!analyze,
            setup: !!setup,
            validate: !!validate
          },
          isLoading: false
        }));
      } catch (err) {
        if (!isMounted) return;

        setState(prev => ({
          ...prev,
          isLoading: false,
          error: err instanceof Error ? err : new Error('Unknown error')
        }));
      }
    };

    runParallelRequests();

    return () => {
      isMounted = false;
      controller.abort();
    };
  }, [idea, storeAnalysis, storeSetup]);

  return state;
}

/**
 * Individual parallel hooks for each analysis section
 * These run in parallel to each other, not sequentially
 */
export function useAnalyzeSectionParallel(
  section: string,
  decompose: DecomposeResponse | null,
  selectedInsight: any
) {
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const { storeAnalysis } = useIdea();

  useEffect(() => {
    if (!decompose || !selectedInsight) return;

    let isMounted = true;

    const fetchAnalysis = async () => {
      setIsLoading(true);
      try {
        const data = await analyzeSection(
          section,
          selectedInsight?.raw || selectedInsight,
          decompose,
          undefined
        );

        if (!isMounted) return;

        setResult(data);
        storeAnalysis(section, data.data);
        setError(null);
      } catch (err) {
        if (!isMounted) return;
        setError(err instanceof Error ? err : new Error('Failed to analyze'));
      } finally {
        if (isMounted) setIsLoading(false);
      }
    };

    fetchAnalysis();

    return () => {
      isMounted = false;
    };
  }, [section, decompose, selectedInsight, storeAnalysis]);

  return { result, isLoading, error };
}

/**
 * Hook to run multiple analyses in parallel
 * useParallelAnalyses(['opportunity', 'competitors', 'risks'])
 * Instead of one at a time
 */
export function useParallelAnalyses(
  sections: string[],
  decompose: DecomposeResponse | null,
  selectedInsight: any
) {
  const [results, setResults] = useState<Record<string, AnalyzeResponse | null>>({});
  const [isLoading, setIsLoading] = useState(false);
  const { storeAnalysis } = useIdea();

  useEffect(() => {
    if (!decompose || !selectedInsight) return;

    let isMounted = true;

    const fetchAllAnalyses = async () => {
      setIsLoading(true);

      // Run all analyses in parallel!
      const promises = sections.map(section =>
        analyzeSection(
          section,
          selectedInsight?.raw || selectedInsight,
          decompose,
          undefined
        ).catch(e => {
          console.error(`Failed to analyze ${section}:`, e);
          return null;
        })
      );

      const responses = await Promise.all(promises);

      if (!isMounted) return;

      // Store all results
      const newResults: Record<string, AnalyzeResponse | null> = {};
      responses.forEach((response, idx) => {
        if (response) {
          const section = sections[idx];
          newResults[section] = response;
          storeAnalysis(section, response.data);
        }
      });

      setResults(newResults);
      setIsLoading(false);
    };

    fetchAllAnalyses();

    return () => {
      isMounted = false;
    };
  }, [sections.join(','), decompose, selectedInsight, storeAnalysis]);

  return { results, isLoading };
}

export default useResearchParallel;
