import { useState, useEffect, useRef, useMemo } from 'react';
import { useIdea } from '@/context/IdeaContext';
import { MOCK_METRICS, MOCK_METHODS } from '@/test/__mocks__/validate';
import { useValidationPlan } from '@/hooks/use-research';
import { useValidationTracking } from '@/hooks/use-validation-tracking';
import { mapValidateCommunities } from '@/lib/transform';
import { useToast } from '@/hooks/use-toast';
import EmptyState from '../common/EmptyState';
import LoadingSpinner from '../common/LoadingSpinner';
import SaveAuthModal from './SaveAuthModal';

type Verdict = 'awaiting' | 'go' | 'pivot' | 'kill';

// Map frontend method IDs to backend channel names
const METHOD_TO_CHANNEL: Record<string, string> = {
  landing: 'landing_page',
  survey: 'survey',
  social: 'whatsapp',
  marketplace: 'marketplace',
  direct: 'whatsapp',
};

export default function ValidateModule() {
  const { idea, selectedInsight } = useIdea();
  const containerRef = useRef<HTMLDivElement>(null);
  const [metrics, setMetrics] = useState(MOCK_METRICS.map((m) => ({ ...m })));
  const [selectedMethods, setSelectedMethods] = useState<Set<string>>(new Set());
  const [sharedChannels, setSharedChannels] = useState<Set<string>>(new Set());
  const [hoveredMetric, setHoveredMetric] = useState<string | null>(null);
  const [hoveredMethod, setHoveredMethod] = useState<string | null>(null);
  const [hoveredChannel, setHoveredChannel] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'current' | 'history'>('current');
  const [showAuthModal, setShowAuthModal] = useState(false);
  const { toast } = useToast();
  const { experiments, saveExperiment, updateMetrics, isLoading: isSaving } = useValidationTracking();
  const isAuthenticated = localStorage.getItem('auth_token');

  // Convert selected methods to backend channels
  const channels = Array.from(selectedMethods)
    .map((method) => METHOD_TO_CHANNEL[method])
    .filter(Boolean);

  const validationQuery = useValidationPlan(undefined, undefined, channels.length > 0 ? channels : undefined);

  // Handle save experiment
  const handleSaveExperiment = async () => {
    // If not authenticated, show login modal
    if (!isAuthenticated) {
      setShowAuthModal(true);
      return;
    }

    if (!idea) {
      toast({
        title: 'Error',
        description: 'No idea selected',
        variant: 'destructive',
      });
      return;
    }

    try {
      await saveExperiment(idea, Array.from(selectedMethods), {
        waitlist_signups: metrics.find((m) => m.id === 'signups')?.actual || 0,
        survey_completions: metrics.find((m) => m.id === 'survey')?.actual || 0,
        would_switch_rate: metrics.find((m) => m.id === 'switch')?.actual || 0,
        price_tolerance_avg: metrics.find((m) => m.id === 'price')?.actual || 0,
        community_engagement: metrics.find((m) => m.id === 'engagement')?.actual || 0,
        reddit_upvotes: metrics.find((m) => m.id === 'reddit')?.actual || 0,
      });

      toast({
        title: 'Experiment saved',
        description: 'Your validation metrics have been saved to the dashboard',
      });

      setActiveTab('history');
    } catch (error) {
      toast({
        title: 'Failed to save',
        description: error instanceof Error ? error.message : 'Unknown error',
        variant: 'destructive',
      });
    }
  };

  const communities = mapValidateCommunities(validationQuery.data) || [];

  useEffect(() => {
    if (validationQuery.error) {
      toast({
        title: 'Validation plan unavailable',
        description: validationQuery.error instanceof Error ? validationQuery.error.message : 'Unexpected error',
        variant: 'destructive',
      });
    }
  }, [validationQuery.error, toast]);

  useEffect(() => {
    const el = containerRef.current;
    if (el) requestAnimationFrame(() => el.classList.add('visible'));
  }, []);

  const updateMetric = (id: string, val: number) => {
    setMetrics((prev) => prev.map((m) => (m.id === id ? { ...m, actual: val } : m)));
  };

  const toggleMethod = (id: string) => {
    setSelectedMethods((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const toggleChannel = (id: string) => {
    setSharedChannels((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const { verdict, reasoning } = useMemo(() => {
    const signups = metrics.find((m) => m.id === 'signups')?.actual || 0;
    const switchRate = metrics.find((m) => m.id === 'switch')?.actual || 0;
    const price = metrics.find((m) => m.id === 'price')?.actual || 0;
    const hasData = signups > 0 || switchRate > 0 || price > 0;

    if (!hasData) return { verdict: 'awaiting' as Verdict, reasoning: 'Enter your experiment results to get a recommendation.' };

    if (signups >= 150 && switchRate >= 60 && price >= 8)
      return { verdict: 'go' as Verdict, reasoning: 'Strong demand signal with healthy price tolerance. Move forward with confidence.' };

    if (signups < 30 && switchRate < 30)
      return { verdict: 'kill' as Verdict, reasoning: 'Low interest across channels. Consider a fundamentally different value proposition.' };

    if (signups >= 80 && switchRate >= 40)
      return { verdict: 'pivot' as Verdict, reasoning: 'Moderate interest — refine positioning, adjust pricing, or narrow the segment.' };

    if (price < 6 && signups > 50)
      return { verdict: 'pivot' as Verdict, reasoning: 'Strong interest but low price tolerance — consider repositioning pricing.' };

    return { verdict: 'pivot' as Verdict, reasoning: 'Mixed signals. Some interest exists but key metrics need improvement.' };
  }, [metrics]);

  // Derived signals
  const signupsVal = metrics.find((m) => m.id === 'signups')?.actual || 0;
  const switchVal = metrics.find((m) => m.id === 'switch')?.actual || 0;
  const priceVal = metrics.find((m) => m.id === 'price')?.actual || 0;
  const demandStrength = signupsVal >= 100 ? 'High' : signupsVal >= 50 ? 'Medium' : 'Low';
  const priceAcceptance = priceVal >= 10 ? 'Strong' : priceVal >= 7 ? 'Moderate' : 'Weak';
  const conversionEst = signupsVal > 0 ? Math.round((switchVal / 100) * signupsVal) : 0;

  const verdictConfig: Record<Verdict, { label: string; color: string; bg: string }> = {
    awaiting: { label: 'Awaiting data', color: 'var(--text-muted)', bg: 'var(--surface-input)' },
    go: { label: 'GO', color: '#2D8B75', bg: 'rgba(45,139,117,0.06)' },
    pivot: { label: 'PIVOT', color: '#D4880F', bg: 'rgba(212,136,15,0.06)' },
    kill: { label: 'NOT WORTH IT', color: '#E05252', bg: 'rgba(224,82,82,0.06)' },
  };
  const vc = verdictConfig[verdict];

  const insightTitle = selectedInsight?.title || 'Existing juice bars are overpriced for basic smoothies';

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
            <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.04em', marginBottom: 4 }}>TESTING</p>
            <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 14, fontWeight: 400, color: 'var(--text-primary)', lineHeight: 1.4 }}>
              {insightTitle}
            </p>
          </div>
          <div>
            <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.04em', marginBottom: 4 }}>METHODS</p>
            <div
              className="flex items-center justify-center rounded-[8px]"
              style={{
                minWidth: 40, height: 40,
                padding: '0 12px',
                backgroundColor: 'rgba(108,92,231,0.06)',
                fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 400, color: 'var(--accent-purple)',
              }}
            >
              {selectedMethods.size}
            </div>
          </div>
        </div>
      </div>

      {/* Intro */}
      <div className="mb-12">
        <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.06em', marginBottom: 10 }}>
          DEMAND VALIDATION
        </p>
        <p className="font-heading" style={{ fontSize: 26, marginBottom: 12 }}>
          Will people actually pay for this?
        </p>
        <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 15, fontWeight: 300, lineHeight: 1.75, color: 'var(--text-secondary)', maxWidth: 540 }}>
          Pick how you want to test demand, track real responses, and get a clear go/no-go signal.
        </p>
      </div>

      {/* VERDICT CARD (hero position) */}
      <div
        className="rounded-[16px] mb-16 text-center"
        style={{ padding: 40, backgroundColor: vc.bg }}
      >
        <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.08em', marginBottom: 14 }}>VERDICT</p>
        <p style={{ fontFamily: "'Instrument Serif', serif", fontSize: 26, fontWeight: 400, color: vc.color, letterSpacing: '-0.02em', lineHeight: 1.25, marginBottom: 16 }}>
          {vc.label}
        </p>
        <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 14, fontWeight: 300, color: 'var(--text-secondary)', lineHeight: 1.75, maxWidth: 480, margin: '0 auto' }}>
          {reasoning}
        </p>
      </div>

      {/* METRICS GRID */}
      <div className="mb-16">
        <p className="font-caption mb-5" style={{ fontSize: 11, letterSpacing: '0.06em' }}>EXPERIMENT METRICS</p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: 12 }}>
          {metrics.map((m) => {
            const pct = Math.min((m.actual / m.target) * 100, 100);
            const barColor = pct >= 100 ? '#2D8B75' : pct >= 50 ? '#D4880F' : 'var(--divider-light)';
            const isHov = hoveredMetric === m.id;
            return (
              <div
                key={m.id}
                className="rounded-[12px] p-5 transition-all duration-200"
                style={{
                  backgroundColor: 'var(--surface-card)',
                  boxShadow: isHov ? '0 4px 16px rgba(0,0,0,0.06)' : '0 1px 3px rgba(0,0,0,0.04)',
                  transform: isHov ? 'translateY(-2px)' : 'translateY(0)',
                }}
                onMouseEnter={() => setHoveredMetric(m.id)}
                onMouseLeave={() => setHoveredMetric(null)}
              >
                <div className="flex items-center justify-between mb-3">
                  <span style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 400, color: 'var(--text-primary)' }}>
                    {m.label}
                  </span>
                  <span className="font-caption" style={{ fontSize: 12 }}>Target: {m.targetLabel}</span>
                </div>
                <div className="flex items-center gap-3 mb-3">
                  <input
                    type="number"
                    value={m.actual || ''}
                    onChange={(e) => updateMetric(m.id, Number(e.target.value) || 0)}
                    placeholder="0"
                    style={{
                      width: 72, padding: '7px 10px', borderRadius: 8,
                      border: '1px solid var(--divider-light)', backgroundColor: 'var(--surface-bg)',
                      fontFamily: "'Inter', sans-serif", fontSize: 15, fontWeight: 400, color: 'var(--text-primary)',
                      outline: 'none',
                    }}
                    onFocus={(e) => { e.currentTarget.style.borderColor = 'var(--accent-purple)'; e.currentTarget.style.boxShadow = '0 0 0 3px rgba(108,92,231,0.08)'; }}
                    onBlur={(e) => { e.currentTarget.style.borderColor = 'var(--divider-light)'; e.currentTarget.style.boxShadow = 'none'; }}
                  />
                  <span className="font-caption" style={{ fontSize: 12 }}>{m.unit}</span>
                </div>
                <div style={{ height: 3, borderRadius: 2, backgroundColor: 'var(--divider-light)', overflow: 'hidden' }}>
                  <div style={{ height: '100%', width: `${pct}%`, backgroundColor: barColor, borderRadius: 2, transition: 'width 300ms ease-out' }} />
                </div>
                <p className="font-caption mt-1.5" style={{ fontSize: 11, textAlign: 'right' }}>
                  {Math.round(pct)}%
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* DERIVED SIGNALS */}
      <div className="mb-16">
        <p className="font-caption mb-5" style={{ fontSize: 11, letterSpacing: '0.06em' }}>DERIVED SIGNALS</p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
          {[
            { label: 'Demand strength', value: demandStrength, color: demandStrength === 'High' ? '#2D8B75' : demandStrength === 'Medium' ? '#D4880F' : '#E05252' },
            { label: 'Est. conversions', value: conversionEst.toString(), color: 'var(--text-primary)' },
            { label: 'Price acceptance', value: priceAcceptance, color: priceAcceptance === 'Strong' ? '#2D8B75' : priceAcceptance === 'Moderate' ? '#D4880F' : '#E05252' },
          ].map((s) => (
            <div key={s.label} className="rounded-[12px] p-5 text-center" style={{ backgroundColor: 'var(--surface-input)' }}>
              <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.05em', marginBottom: 8 }}>{s.label}</p>
              <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 18, fontWeight: 400, color: s.color }}>{s.value}</p>
            </div>
          ))}
        </div>
      </div>

      {/* VALIDATION METHODS */}
      <div className="mb-16">
        <p className="font-caption mb-5" style={{ fontSize: 11, letterSpacing: '0.06em' }}>VALIDATION METHODS</p>
        <div className="flex flex-col gap-2">
          {MOCK_METHODS.map((method) => {
            const isSelected = selectedMethods.has(method.id);
            const isHov = hoveredMethod === method.id;
            return (
              <div
                key={method.id}
                className="rounded-[12px] p-5 transition-all duration-200 cursor-pointer active:scale-[0.98]"
                style={{
                  backgroundColor: isSelected ? 'rgba(108,92,231,0.04)' : 'var(--surface-card)',
                  boxShadow: isSelected
                    ? '0 0 0 1.5px rgba(108,92,231,0.25)'
                    : isHov ? '0 4px 16px rgba(0,0,0,0.06)' : '0 1px 3px rgba(0,0,0,0.04)',
                  transform: isHov ? 'translateY(-1px)' : 'translateY(0)',
                }}
                onMouseEnter={() => setHoveredMethod(method.id)}
                onMouseLeave={() => setHoveredMethod(null)}
                onClick={() => toggleMethod(method.id)}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 14, fontWeight: 400, color: isSelected ? 'var(--accent-purple)' : 'var(--text-primary)', marginBottom: 4 }}>
                      {method.name}
                    </p>
                    <p className="font-caption" style={{ fontSize: 12 }}>{method.description}</p>
                  </div>
                  <div className="flex items-center gap-3 flex-shrink-0 ml-4">
                    <span className="font-caption" style={{ fontSize: 11 }}>
                      {method.effort} effort · {method.speed}
                    </span>
                    <div
                      className="rounded-full transition-all duration-200"
                      style={{
                        width: 20, height: 20,
                        border: isSelected ? 'none' : '1.5px solid var(--divider-light)',
                        backgroundColor: isSelected ? 'var(--accent-purple)' : 'transparent',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                      }}
                    >
                      {isSelected && <span style={{ color: '#fff', fontSize: 11, lineHeight: 1 }}>✓</span>}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* CHANNELS */}
      <div className="mb-16">
        <p className="font-caption mb-5" style={{ fontSize: 11, letterSpacing: '0.06em' }}>WHERE TO SHARE</p>
        {validationQuery.isPending ? (
          <LoadingSpinner message="Finding validation communities..." />
        ) : communities.length === 0 ? (
          <EmptyState message="No communities returned yet." />
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: 10 }}>
            {communities.map((c) => {
              const isShared = sharedChannels.has(c.id);
              const isHov = hoveredChannel === c.id;
              return (
                <div
                  key={c.id}
                  className="rounded-[12px] p-4 transition-all duration-200"
                  style={{
                    backgroundColor: isShared ? 'rgba(45,139,117,0.04)' : 'var(--surface-card)',
                    boxShadow: isHov ? '0 4px 12px rgba(0,0,0,0.06)' : '0 1px 3px rgba(0,0,0,0.04)',
                    transform: isHov ? 'translateY(-1px)' : 'translateY(0)',
                  }}
                  onMouseEnter={() => setHoveredChannel(c.id)}
                  onMouseLeave={() => setHoveredChannel(null)}
                >
                  <div className="flex items-center justify-between mb-2">
                    <a
                      href={c.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      onClick={(e) => e.stopPropagation()}
                      style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 400, color: 'var(--accent-purple)', textDecoration: 'none' }}
                    >
                      {c.name} ↗
                    </a>
                    <span
                      className="font-caption rounded-full px-2 py-0.5"
                      style={{ fontSize: 10, backgroundColor: c.platformColor, color: '#fff' }}
                    >
                      {c.platform}
                    </span>
                  </div>
                  <p className="font-caption" style={{ fontSize: 12, marginBottom: 6 }}>{c.members} members</p>
                  <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 12, fontWeight: 300, color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: 8 }}>
                    {c.rationale}
                  </p>
                  <button
                    onClick={() => toggleChannel(c.id)}
                    className="rounded-[8px] px-3 py-1.5 transition-all duration-200 active:scale-[0.97]"
                    style={{
                      fontSize: 11, fontFamily: "'Inter', sans-serif", fontWeight: 400,
                      backgroundColor: isShared ? 'rgba(45,139,117,0.08)' : 'var(--surface-input)',
                      color: isShared ? '#2D8B75' : 'var(--text-muted)',
                      border: 'none', cursor: 'pointer',
                    }}
                  >
                    {isShared ? '✓ Shared' : 'Mark as shared'}
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* SUMMARY */}
      <div
        className="rounded-[14px] p-6 mb-12"
        style={{ backgroundColor: 'var(--surface-input)' }}
      >
        <p className="font-caption mb-3" style={{ fontSize: 11, letterSpacing: '0.06em' }}>EXPERIMENT SUMMARY</p>
        <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 14, fontWeight: 300, color: 'var(--text-secondary)', lineHeight: 1.75 }}>
          {selectedMethods.size > 0
            ? `You selected ${selectedMethods.size} validation method${selectedMethods.size !== 1 ? 's' : ''} and shared across ${sharedChannels.size} channel${sharedChannels.size !== 1 ? 's' : ''}. ${verdict === 'go' ? 'Strong signals — this idea is worth pursuing.' : verdict === 'kill' ? 'Weak signals — consider pivoting to a different approach.' : verdict === 'pivot' ? 'Mixed signals — refine your positioning before investing further.' : 'Enter your results above to see a recommendation.'}`
            : 'Select validation methods and enter experiment results to generate a summary.'}
        </p>
      </div>

      {/* Tabs for current vs history */}
      <div className="flex gap-4 mb-8" style={{ borderBottom: '1px solid var(--divider)' }}>
        <button
          onClick={() => setActiveTab('current')}
          className="font-caption pb-3 transition-colors duration-200"
          style={{
            fontSize: 13,
            fontWeight: activeTab === 'current' ? 500 : 400,
            color: activeTab === 'current' ? 'var(--accent-purple)' : 'var(--text-muted)',
            borderBottom: activeTab === 'current' ? '2px solid var(--accent-purple)' : 'none',
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            padding: '0 8px',
          }}
        >
          Current Run
        </button>
        <button
          onClick={() => setActiveTab('history')}
          className="font-caption pb-3 transition-colors duration-200"
          style={{
            fontSize: 13,
            fontWeight: activeTab === 'history' ? 500 : 400,
            color: activeTab === 'history' ? 'var(--accent-purple)' : 'var(--text-muted)',
            borderBottom: activeTab === 'history' ? '2px solid var(--accent-purple)' : 'none',
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            padding: '0 8px',
          }}
        >
          Experiment History ({experiments.length})
        </button>
      </div>

      {/* Tab content */}
      {activeTab === 'current' && (
        <>
          {/* Bottom actions */}
          <div
            className="flex flex-wrap items-center gap-3 pt-8"
            style={{ borderTop: '1px solid var(--divider)' }}
          >
            <button
              onClick={handleSaveExperiment}
              disabled={isSaving || metrics.every((m) => m.actual === 0)}
              className="rounded-[12px] px-6 py-3 transition-all duration-200 active:scale-[0.97] disabled:opacity-50 disabled:cursor-not-allowed"
              style={{
                fontFamily: "'Inter', sans-serif", fontSize: 14, fontWeight: 400,
                backgroundColor: 'var(--accent-purple)', color: '#FFFFFF',
                border: 'none', cursor: 'pointer',
              }}
              onMouseEnter={(e) => !isSaving && (e.currentTarget.style.boxShadow = '0 4px 12px rgba(108,92,231,0.3)')}
              onMouseLeave={(e) => (e.currentTarget.style.boxShadow = 'none')}
            >
              {isSaving ? 'Saving...' : 'Save validation results'}
            </button>
            <button
              className="rounded-[12px] px-5 py-3 transition-all duration-200 active:scale-[0.97]"
              style={{
                fontFamily: "'Inter', sans-serif", fontSize: 14, fontWeight: 400,
                backgroundColor: 'rgba(108,92,231,0.06)', color: 'var(--accent-purple)',
                border: 'none', cursor: 'pointer',
              }}
              onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'rgba(108,92,231,0.12)')}
              onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'rgba(108,92,231,0.06)')}
            >
              Export report
            </button>
            <button
              className="rounded-[12px] px-5 py-3 transition-all duration-200 active:scale-[0.97]"
              style={{
                fontFamily: "'Inter', sans-serif", fontSize: 14, fontWeight: 300,
                backgroundColor: 'transparent', color: 'var(--text-secondary)',
                border: '1px solid var(--divider-light)', cursor: 'pointer',
              }}
            >
              Start new idea
            </button>
          </div>
        </>
      )}

      {/* History Tab */}
      {activeTab === 'history' && (
        <div className="py-8">
          {experiments.length === 0 ? (
            <EmptyState message="No validation experiments yet. Run your first validation and save the results." />
          ) : (
            <div className="flex flex-col gap-4">
              {experiments.map((exp, idx) => (
                <div
                  key={exp.id}
                  className="rounded-[12px] p-5 transition-all duration-200 hover:shadow-md"
                  style={{
                    backgroundColor: 'var(--surface-card)',
                    boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
                  }}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 500, color: 'var(--text-primary)', marginBottom: 4 }}>
                        Experiment {experiments.length - idx}
                      </p>
                      <p className="font-caption" style={{ fontSize: 12 }}>
                        {exp.created_at ? new Date(exp.created_at).toLocaleDateString() : 'Date unknown'}
                      </p>
                    </div>
                    <div
                      className="rounded-[8px] px-3 py-1.5"
                      style={{
                        backgroundColor:
                          exp.verdict === 'go'
                            ? 'rgba(45,139,117,0.06)'
                            : exp.verdict === 'kill'
                              ? 'rgba(224,82,82,0.06)'
                              : 'rgba(212,136,15,0.06)',
                        color:
                          exp.verdict === 'go'
                            ? '#2D8B75'
                            : exp.verdict === 'kill'
                              ? '#E05252'
                              : '#D4880F',
                        fontFamily: "'Inter', sans-serif",
                        fontSize: 12,
                        fontWeight: 500,
                      }}
                    >
                      {exp.verdict?.toUpperCase() || 'AWAITING'}
                    </div>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 12, marginBottom: 12 }}>
                    <div>
                      <p className="font-caption" style={{ fontSize: 11, marginBottom: 4 }}>Signups</p>
                      <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 16, fontWeight: 500, color: 'var(--text-primary)' }}>
                        {exp.waitlist_signups}
                      </p>
                    </div>
                    <div>
                      <p className="font-caption" style={{ fontSize: 11, marginBottom: 4 }}>Switch Rate</p>
                      <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 16, fontWeight: 500, color: 'var(--text-primary)' }}>
                        {exp.would_switch_rate.toFixed(0)}%
                      </p>
                    </div>
                    <div>
                      <p className="font-caption" style={{ fontSize: 11, marginBottom: 4 }}>Price Tolerance</p>
                      <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 16, fontWeight: 500, color: 'var(--text-primary)' }}>
                        ${exp.price_tolerance_avg.toFixed(2)}
                      </p>
                    </div>
                  </div>

                  {exp.methods.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {exp.methods.map((method) => (
                        <span
                          key={method}
                          className="rounded-full px-2.5 py-1 font-caption"
                          style={{
                            fontSize: 11,
                            backgroundColor: 'rgba(108,92,231,0.06)',
                            color: 'var(--accent-purple)',
                          }}
                        >
                          {method}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Auth modal for saving without account */}
      <SaveAuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        onSaveSuccess={handleSaveExperiment}
      />
    </div>
  );
}


