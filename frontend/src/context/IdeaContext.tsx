import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';
import type { Insight } from '@/test/__mocks__/discover';

export type Step = 'discover' | 'analyze' | 'setup' | 'validate';

interface PipelineContext {
  /** Accumulated analysis results keyed by section */
  analysisContext: Record<string, unknown>;
  /** Setup module results */
  setupContext: Record<string, unknown> | null;
}

interface IdeaState {
  idea: string;
  setIdea: (idea: string) => void;
  currentStep: Step;
  setCurrentStep: (step: Step) => void;
  selectedInsight: Insight | null;
  setSelectedInsight: (insight: Insight | null) => void;
  /** Store analysis section result for downstream modules */
  storeAnalysis: (section: string, data: unknown) => void;
  /** Store full setup result for validate module */
  storeSetup: (data: Record<string, unknown>) => void;
  pipeline: PipelineContext;
}

const IdeaContext = createContext<IdeaState | null>(null);

export function IdeaProvider({ children }: { children: ReactNode }) {
  const [idea, setIdea] = useState('');
  const [currentStep, setCurrentStep] = useState<Step>('discover');
  const [selectedInsight, setSelectedInsight] = useState<Insight | null>(null);
  const [pipeline, setPipeline] = useState<PipelineContext>({
    analysisContext: {},
    setupContext: null,
  });

  const storeAnalysis = useCallback((section: string, data: unknown) => {
    setPipeline((prev) => ({
      ...prev,
      analysisContext: { ...prev.analysisContext, [section]: data },
    }));
  }, []);

  const storeSetup = useCallback((data: Record<string, unknown>) => {
    setPipeline((prev) => ({ ...prev, setupContext: data }));
  }, []);

  return (
    <IdeaContext.Provider
      value={{
        idea,
        setIdea,
        currentStep,
        setCurrentStep,
        selectedInsight,
        setSelectedInsight,
        storeAnalysis,
        storeSetup,
        pipeline,
      }}
    >
      {children}
    </IdeaContext.Provider>
  );
}

export function useIdea() {
  const ctx = useContext(IdeaContext);
  if (!ctx) throw new Error('useIdea must be used within IdeaProvider');
  return ctx;
}
