import { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { useIdea } from '@/context/IdeaContext';
import type { TimelinePhase } from '@/types/research-ui';
import { useSetupPlan } from '@/hooks/use-research';
import { mapSetupTiers, mapSetupSuppliers, mapSetupTeam, mapSetupTimeline } from '@/lib/transform';
import { useToast } from '@/hooks/use-toast';
import EmptyState from '../common/EmptyState';
import CostBuilder from './CostBuilder';
import Suppliers from './Suppliers';
import TeamBuilder from './TeamBuilder';
import LaunchTimeline from './LaunchTimeline';
import PlanSummary from './PlanSummary';

type Estimate = 'low' | 'mid' | 'high';

const TABS = [
  { key: 'costs', label: 'Costs' },
  { key: 'suppliers', label: 'Suppliers' },
  { key: 'team', label: 'Team' },
  { key: 'timeline', label: 'Timeline' },
  { key: 'summary', label: 'Summary' },
] as const;

type TabKey = typeof TABS[number]['key'];

const TAB_QUESTIONS: Record<TabKey, string> = {
  costs: 'What will it cost to launch?',
  suppliers: 'Who are the local partners?',
  team: 'Who do you need to hire?',
  timeline: 'How long will it take?',
  summary: 'What does the full plan look like?',
};

export default function SetupModule() {
  const { idea, selectedInsight } = useIdea();
  const containerRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();

  const setupQuery = useSetupPlan();
  useEffect(() => {
    if (setupQuery.error) {
      toast({
        title: 'Setup plan unavailable',
        description: setupQuery.error instanceof Error ? setupQuery.error.message : 'Unexpected error.',
        variant: 'destructive',
      });
    }
  }, [setupQuery.error, toast]);

  const mapped = useMemo(() => mapSetupTiers(setupQuery.data), [setupQuery.data]);
  const supplierData = useMemo(() => mapSetupSuppliers(setupQuery.data) || undefined, [setupQuery.data]);
  const teamData = useMemo(() => mapSetupTeam(setupQuery.data) || undefined, [setupQuery.data]);
  const timelineData = useMemo(() => mapSetupTimeline(setupQuery.data) || [], [setupQuery.data]);

  const [activeTab, setActiveTab] = useState<TabKey>('costs');
  const [selectedTier, setSelectedTier] = useState('recommended');
  const [estimates, setEstimates] = useState<Record<string, Estimate>>({});
  const [includedRoles, setIncludedRoles] = useState<Set<string>>(new Set(['manager', 'barista']));
  const [phases, setPhases] = useState<TimelinePhase[]>(timelineData.map((p) => ({ ...p, tasks: p.tasks.map((t) => ({ ...t })) })));

  useEffect(() => {
    if (timelineData.length) {
      setPhases(timelineData.map((p) => ({ ...p, tasks: p.tasks.map((t) => ({ ...t })) })));
    }
  }, [timelineData]);

  useEffect(() => {
    const el = containerRef.current;
    if (el) requestAnimationFrame(() => el.classList.add('visible'));
  }, []);

  const handleEstimateChange = useCallback((itemLabel: string, est: Estimate) => {
    setEstimates((prev) => ({ ...prev, [itemLabel]: est }));
  }, []);

  const handleToggleRole = useCallback((id: string) => {
    setIncludedRoles((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  }, []);

  const handleToggleTask = useCallback((phaseId: string, taskId: string) => {
    setPhases((prev) =>
      prev.map((p) =>
        p.id === phaseId
          ? { ...p, tasks: p.tasks.map((t) => (t.id === taskId ? { ...t, completed: !t.completed } : t)) }
          : p
      )
    );
  }, []);

  const tierCosts = mapped?.costs || {};
  const tierList = mapped?.tiers || [];

  const currentTotal = useMemo(() => {
    const categories = tierCosts[selectedTier] || [];
    let total = 0;
    categories.forEach((cat) =>
      cat.items.forEach((item) => {
        total += item[estimates[item.label] || 'mid'];
      })
    );
    return total;
  }, [selectedTier, estimates]);

  const insightTitle = selectedInsight?.title || 'Existing juice bars are overpriced for basic smoothies';

  const isLoading = setupQuery.isLoading;

  const renderTab = () => {
    if (isLoading) {
      return <SectionSkeleton />;
    }
    switch (activeTab) {
      case 'costs':
        return tierList.length ? (
          <CostBuilder
            selectedTier={selectedTier}
            onSelectTier={setSelectedTier}
            estimates={estimates}
            onEstimateChange={handleEstimateChange}
            tiers={tierList}
            tierCosts={tierCosts}
          />
        ) : (
          <EmptyState message="No cost tiers available yet." />
        );
      case 'suppliers':
        return (
          <div>
            <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.06em', marginBottom: 16 }}>
              SUPPLIERS & PARTNERS
            </p>
            {supplierData ? <Suppliers suppliers={supplierData} /> : <EmptyState message="No suppliers returned." />}
          </div>
        );
      case 'team':
        return teamData ? (
          <TeamBuilder includedRoles={includedRoles} onToggleRole={handleToggleRole} team={teamData || undefined} />
        ) : (
          <EmptyState message="No team plan yet." />
        );
      case 'timeline':
        return (
          <div>
            <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.06em', marginBottom: 20 }}>
              LAUNCH TIMELINE
            </p>
            {phases.length ? <LaunchTimeline phases={phases} onToggleTask={handleToggleTask} /> : <EmptyState message="No timeline provided." />}
          </div>
        );
      case 'summary':
        return (
          <PlanSummary
            selectedTier={selectedTier}
            currentTotal={currentTotal}
            includedRoles={includedRoles}
            phases={phases}
            tiers={tierList}
            team={teamData}
          />
        );
    }
  };

  return (
    <div ref={containerRef} className="scroll-reveal" style={{ maxWidth: 800, margin: '0 auto', padding: '0 24px' }}>
      {/* Sticky context strip */}
      <div
        className="sticky z-30 rounded-[12px] mb-12 p-5"
        style={{
          top: 80,
          backgroundColor: 'rgba(255,255,255,0.85)',
          backdropFilter: 'blur(16px)',
          boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
        }}
      >
        <div className="flex flex-wrap items-start gap-x-10 gap-y-3">
          <div className="min-w-0 flex-1">
            <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.04em', marginBottom: 4 }}>IDEA</p>
            <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 14, fontWeight: 400, color: 'var(--text-primary)', lineHeight: 1.4 }}>
              {idea}
            </p>
          </div>
          <div className="min-w-0 flex-1">
            <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.04em', marginBottom: 4 }}>SELECTED OPPORTUNITY</p>
            <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 14, fontWeight: 400, color: 'var(--text-primary)', lineHeight: 1.4 }}>
              {insightTitle}
            </p>
          </div>
          <div>
            <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.04em', marginBottom: 4 }}>MODEL</p>
            <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 400, color: 'var(--accent-purple)' }}>
              {tierList.find((t) => t.id === selectedTier)?.title}
            </p>
          </div>
        </div>
      </div>

      {/* Intro */}
      <div className="mb-10">
        <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.06em', marginBottom: 10 }}>
          LAUNCH PLAN
        </p>
        <p className="font-heading" style={{ fontSize: 26, marginBottom: 12 }}>
          How would you actually start this?
        </p>
        <p
          style={{
            fontFamily: "'Inter', sans-serif",
            fontSize: 15,
            fontWeight: 300,
            lineHeight: 1.75,
            color: 'var(--text-secondary)',
            maxWidth: 540,
          }}
        >
          We mapped out costs, suppliers, team, and a realistic launch timeline for this opportunity.
        </p>
      </div>

      {/* Tab switcher */}
      <div className="mb-10">
        <div
          className="flex gap-1 overflow-x-auto hide-scrollbar pb-1"
          style={{ borderBottom: '1px solid var(--divider)' }}
        >
          {TABS.map((tab) => {
            const isActive = activeTab === tab.key;
            return (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className="relative px-4 py-3 transition-all duration-200 active:scale-[0.97] whitespace-nowrap"
                style={{
                  fontFamily: "'Inter', sans-serif",
                  fontSize: 13,
                  fontWeight: isActive ? 400 : 300,
                  color: isActive ? 'var(--accent-purple)' : 'var(--text-muted)',
                  backgroundColor: 'transparent',
                  border: 'none',
                  cursor: 'pointer',
                }}
              >
                {tab.label}
                {isActive && (
                  <div
                    style={{
                      position: 'absolute',
                      bottom: -1,
                      left: 16,
                      right: 16,
                      height: 1.5,
                      backgroundColor: 'var(--accent-purple)',
                      borderRadius: 1,
                    }}
                  />
                )}
              </button>
            );
          })}
        </div>

        {/* Tab question */}
        <p
          className="mt-6 mb-8"
          style={{
            fontFamily: "'Instrument Serif', serif",
            fontSize: 18,
            fontStyle: 'italic',
            color: 'var(--text-secondary)',
          }}
        >
          {TAB_QUESTIONS[activeTab]}
        </p>
      </div>

      {/* Tab content */}
      <div className="mb-16" style={{ minHeight: 300 }}>
        {renderTab()}
      </div>

      {/* Bottom actions */}
      <div
        className="flex flex-wrap items-center gap-3 mt-8 pt-8"
        style={{ borderTop: '1px solid var(--divider)' }}
      >
        <button
          className="rounded-[12px] px-5 py-3 transition-all duration-200 active:scale-[0.97]"
          style={{
            fontFamily: "'Inter', sans-serif",
            fontSize: 14,
            fontWeight: 400,
            backgroundColor: 'rgba(108,92,231,0.06)',
            color: 'var(--accent-purple)',
            border: 'none',
            cursor: 'pointer',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'rgba(108,92,231,0.12)')}
          onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'rgba(108,92,231,0.06)')}
        >
          Save plan
        </button>
        <button
          className="rounded-[12px] px-5 py-3 transition-all duration-200 active:scale-[0.97]"
          style={{
            fontFamily: "'Inter', sans-serif",
            fontSize: 14,
            fontWeight: 300,
            backgroundColor: 'transparent',
            color: 'var(--text-secondary)',
            border: '1px solid var(--divider-light)',
            cursor: 'pointer',
          }}
        >
          Adjust assumptions
        </button>
      </div>
    </div>
  );
}
