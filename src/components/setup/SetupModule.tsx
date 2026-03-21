import { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { useIdea } from '@/context/IdeaContext';
import { MOCK_TIERS, MOCK_TIER_COSTS, MOCK_TIMELINE } from '@/data/setup-mock';
import type { TimelinePhase } from '@/data/setup-mock';
import CostBuilder from './CostBuilder';
import Suppliers from './Suppliers';
import TeamBuilder from './TeamBuilder';
import LaunchTimeline from './LaunchTimeline';
import PlanSummary from './PlanSummary';

type Estimate = 'low' | 'mid' | 'high';

export default function SetupModule() {
  const { idea, selectedInsight } = useIdea();
  const containerRef = useRef<HTMLDivElement>(null);

  const [selectedTier, setSelectedTier] = useState('recommended');
  const [estimates, setEstimates] = useState<Record<string, Estimate>>({});
  const [includedRoles, setIncludedRoles] = useState<Set<string>>(new Set(['manager', 'barista']));
  const [phases, setPhases] = useState<TimelinePhase[]>(MOCK_TIMELINE.map((p) => ({ ...p, tasks: p.tasks.map((t) => ({ ...t })) })));

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

  const currentTotal = useMemo(() => {
    const categories = MOCK_TIER_COSTS[selectedTier] || [];
    let total = 0;
    categories.forEach((cat) =>
      cat.items.forEach((item) => {
        total += item[estimates[item.label] || 'mid'];
      })
    );
    return total;
  }, [selectedTier, estimates]);

  const insightTitle = selectedInsight || 'Existing juice bars are overpriced for basic smoothies';

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
              {MOCK_TIERS.find((t) => t.id === selectedTier)?.title}
            </p>
          </div>
        </div>
      </div>

      {/* Intro */}
      <div className="mb-16">
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

      {/* Cost Builder */}
      <div className="mb-20">
        <CostBuilder
          selectedTier={selectedTier}
          onSelectTier={setSelectedTier}
          estimates={estimates}
          onEstimateChange={handleEstimateChange}
        />
      </div>

      {/* Suppliers */}
      <div className="mb-20">
        <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.06em', marginBottom: 16 }}>
          SUPPLIERS & PARTNERS
        </p>
        <Suppliers />
      </div>

      {/* Team Builder */}
      <div className="mb-20">
        <TeamBuilder includedRoles={includedRoles} onToggleRole={handleToggleRole} />
      </div>

      {/* Launch Timeline */}
      <div className="mb-20">
        <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.06em', marginBottom: 20 }}>
          LAUNCH TIMELINE
        </p>
        <LaunchTimeline phases={phases} onToggleTask={handleToggleTask} />
      </div>

      {/* Plan Summary */}
      <div className="mb-16">
        <PlanSummary
          selectedTier={selectedTier}
          currentTotal={currentTotal}
          includedRoles={includedRoles}
          phases={phases}
        />
      </div>

      {/* Bottom actions */}
      <div
        className="flex flex-wrap items-center gap-3 mt-20 pt-8"
        style={{ borderTop: '1px solid var(--divider)' }}
      >
        <button
          className="rounded-[12px] px-6 py-3 transition-all duration-200 active:scale-[0.97]"
          style={{
            fontFamily: "'Inter', sans-serif",
            fontSize: 14,
            fontWeight: 400,
            backgroundColor: 'var(--accent-purple)',
            color: '#FFFFFF',
            border: 'none',
            cursor: 'pointer',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.boxShadow = '0 4px 12px rgba(108,92,231,0.3)')}
          onMouseLeave={(e) => (e.currentTarget.style.boxShadow = 'none')}
        >
          Create validation plan →
        </button>
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
