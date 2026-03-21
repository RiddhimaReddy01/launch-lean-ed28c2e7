import { createContext, useContext, useState, type ReactNode } from 'react';
import type { Insight } from '@/test/__mocks__/discover';

export type Step = 'discover' | 'analyze' | 'setup' | 'validate';

interface IdeaState {
  idea: string;
  setIdea: (idea: string) => void;
  currentStep: Step;
  setCurrentStep: (step: Step) => void;
  selectedInsight: Insight | null;
  setSelectedInsight: (insight: Insight | null) => void;
}

const IdeaContext = createContext<IdeaState | null>(null);

export function IdeaProvider({ children }: { children: ReactNode }) {
  const [idea, setIdea] = useState('');
  const [currentStep, setCurrentStep] = useState<Step>('discover');
  const [selectedInsight, setSelectedInsight] = useState<Insight | null>(null);

  return (
    <IdeaContext.Provider value={{ idea, setIdea, currentStep, setCurrentStep, selectedInsight, setSelectedInsight }}>
      {children}
    </IdeaContext.Provider>
  );
}

export function useIdea() {
  const ctx = useContext(IdeaContext);
  if (!ctx) throw new Error('useIdea must be used within IdeaProvider');
  return ctx;
}
