import { useState, useEffect, useRef, useMemo } from 'react';
import { useIdea } from '@/context/IdeaContext';
import type { MetricTarget, ValidationMethod, CommunityChannel } from '@/types/research-ui';
import { VALIDATION_METHODS, createDefaultValidationMetrics } from '@/lib/research-ui-config';
import { useValidationPlan } from '@/hooks/use-research';
import { mapValidateCommunities } from '@/lib/transform';
import { useToast } from '@/hooks/use-toast';

type Verdict = 'awaiting' | 'go' | 'pivot' | 'kill';

const METHOD_CATEGORIES = [
  { key: 'all', label: 'All methods' },
  { key: 'build', label: 'Build' },
  { key: 'outreach', label: 'Outreach' },
  { key: 'social', label: 'Social' },
  { key: 'paid', label: 'Paid ads' },
] as const;

export default function ValidateModule() {
  const { idea, selectedInsight } = useIdea();
  const containerRef = useRef<HTMLDivElement>(null);
  const [metrics, setMetrics] = useState<MetricTarget[]>(createDefaultValidationMetrics());
  const [selectedMethod, setSelectedMethod] = useState<string>('');
  const [activeChannels, setActiveChannels] = useState<Set<string>>(new Set());
  const { toast } = useToast();
  const validationQuery = useValidationPlan();

  const communities: CommunityChannel[] = mapValidateCommunities(validationQuery.data) || [];

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

  const toggleChannel = (id: string) => {
    setActiveChannels((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const currentMethod = VALIDATION_METHODS.find((m) => m.id === selectedMethod);

  const handleMethodAction = (method: ValidationMethod) => {
    if (method.action === 'lovable') {
      const prompt = encodeURIComponent(
        `Create a landing page for: ${idea}. Include a waitlist signup form, headline, value proposition, and social proof section.`
      );
      window.open(`https://lovable.dev/projects/create?prompt=${prompt}`, '_blank');
    }
  };

  // Verdict engine
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

  const verdictConfig: Record<Verdict, { label: string; color: string; bg: string; border: string }> = {
    awaiting: { label: 'Awaiting data', color: 'var(--text-muted)', bg: 'var(--surface-input)', border: 'var(--divider)' },
    go: { label: 'GO', color: '#1a7a63', bg: 'rgba(45,139,117,0.06)', border: 'rgba(45,139,117,0.15)' },
    pivot: { label: 'PIVOT', color: '#b87a0a', bg: 'rgba(212,136,15,0.06)', border: 'rgba(212,136,15,0.15)' },
    kill: { label: 'NOT VIABLE', color: '#c43c3c', bg: 'rgba(224,82,82,0.06)', border: 'rgba(224,82,82,0.15)' },
  };
  const vc = verdictConfig[verdict];

  return (
    <div ref={containerRef} className="scroll-reveal" style={{ maxWidth: 880, margin: '0 auto', padding: '0 24px' }}>

      {/* ── HEADER ── */}
      <div style={{ marginBottom: 40 }}>
        <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.06em', marginBottom: 10 }}>
          DEMAND VALIDATION
        </p>
        <p className="font-heading" style={{ fontSize: 26, marginBottom: 8 }}>
          Will people actually pay for this?
        </p>
        <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 14, fontWeight: 300, lineHeight: 1.7, color: 'var(--text-secondary)', maxWidth: 520 }}>
          Choose a method, track real responses, and get a clear go/no-go signal.
        </p>
      </div>

      {/* ── STEP 1: METHOD SELECTOR (dropdown) ── */}
      <div style={{ marginBottom: 48 }}>
        <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.06em', marginBottom: 14 }}>
          1 · CHOOSE YOUR METHOD
        </p>
        <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start', flexWrap: 'wrap' }}>
          <select
            value={selectedMethod}
            onChange={(e) => setSelectedMethod(e.target.value)}
            style={{
              flex: '1 1 280px',
              maxWidth: 400,
              padding: '12px 16px',
              borderRadius: 12,
              border: '1px solid var(--divider-light)',
              backgroundColor: 'var(--surface-card)',
              fontFamily: "'Inter', sans-serif",
              fontSize: 14,
              fontWeight: 400,
              color: selectedMethod ? 'var(--text-primary)' : 'var(--text-muted)',
              outline: 'none',
              cursor: 'pointer',
              appearance: 'none',
              backgroundImage: `url("data:image/svg+xml,%3Csvg width='12' height='8' viewBox='0 0 12 8' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1.5L6 6.5L11 1.5' stroke='%239B9B9B' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E")`,
              backgroundRepeat: 'no-repeat',
              backgroundPosition: 'right 14px center',
              paddingRight: 40,
            }}
          >
            <option value="">Select a validation method…</option>
            <optgroup label="Build">
              {VALIDATION_METHODS.filter((m) => m.category === 'build').map((m) => (
                <option key={m.id} value={m.id}>{m.name}</option>
              ))}
            </optgroup>
            <optgroup label="Outreach">
              {VALIDATION_METHODS.filter((m) => m.category === 'outreach').map((m) => (
                <option key={m.id} value={m.id}>{m.name}</option>
              ))}
            </optgroup>
            <optgroup label="Social">
              {VALIDATION_METHODS.filter((m) => m.category === 'social').map((m) => (
                <option key={m.id} value={m.id}>{m.name}</option>
              ))}
            </optgroup>
            <optgroup label="Paid Ads">
              {VALIDATION_METHODS.filter((m) => m.category === 'paid').map((m) => (
                <option key={m.id} value={m.id}>{m.name}</option>
              ))}
            </optgroup>
          </select>

          {currentMethod?.action === 'lovable' && (
            <button
              onClick={() => handleMethodAction(currentMethod)}
              className="transition-all duration-200 active:scale-[0.97]"
              style={{
                padding: '12px 20px',
                borderRadius: 12,
                border: 'none',
                backgroundColor: 'var(--accent-purple)',
                color: '#fff',
                fontFamily: "'Inter', sans-serif",
                fontSize: 13,
                fontWeight: 500,
                cursor: 'pointer',
                whiteSpace: 'nowrap',
              }}
            >
              Open in Lovable →
            </button>
          )}
        </div>

        {/* Method detail card */}
        {currentMethod && (
          <div
            className="mt-3 rounded-xl p-4"
            style={{
              backgroundColor: 'var(--surface-card)',
              border: '1px solid var(--divider-light)',
              maxWidth: 400,
            }}
          >
            <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 400, color: 'var(--text-primary)', marginBottom: 4 }}>
              {currentMethod.name}
            </p>
            <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 12, fontWeight: 300, color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: 8 }}>
              {currentMethod.description}
            </p>
            <div className="flex gap-2">
              <span
                className="rounded-md px-2 py-0.5"
                style={{
                  fontSize: 11,
                  fontFamily: "'Inter', sans-serif",
                  fontWeight: 400,
                  color: currentMethod.effort === 'low' ? '#1a7a63' : currentMethod.effort === 'medium' ? '#b87a0a' : '#c43c3c',
                  backgroundColor: currentMethod.effort === 'low' ? 'rgba(45,139,117,0.08)' : currentMethod.effort === 'medium' ? 'rgba(212,136,15,0.08)' : 'rgba(224,82,82,0.08)',
                }}
              >
                {currentMethod.effort} effort
              </span>
              <span
                className="rounded-md px-2 py-0.5"
                style={{
                  fontSize: 11,
                  fontFamily: "'Inter', sans-serif",
                  fontWeight: 300,
                  color: 'var(--text-muted)',
                  backgroundColor: 'var(--surface-input)',
                }}
              >
                {currentMethod.speed === 'fast' ? '⚡ Fast' : currentMethod.speed === 'medium' ? '⏱ Medium' : '🐢 Slow'}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* ── STEP 2: EXPERIMENT DASHBOARD ── */}
      <div style={{ marginBottom: 48 }}>
        <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.06em', marginBottom: 14 }}>
          2 · EXPERIMENT DASHBOARD
        </p>

        {/* KPI Cards Row */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: 12, marginBottom: 20 }}>
          {metrics.map((m) => {
            const pct = Math.min((m.actual / m.target) * 100, 100);
            const statusColor = pct >= 100 ? '#1a7a63' : pct >= 50 ? '#b87a0a' : pct > 0 ? '#c43c3c' : 'var(--text-muted)';

            return (
              <div
                key={m.id}
                className="rounded-xl p-4"
                style={{ backgroundColor: 'var(--surface-card)', border: '1px solid var(--divider-light)' }}
              >
                <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 11, fontWeight: 300, color: 'var(--text-muted)', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                  {m.label}
                </p>
                <div className="flex items-baseline gap-1.5" style={{ marginBottom: 10 }}>
                  <input
                    type="number"
                    value={m.actual || ''}
                    onChange={(e) => updateMetric(m.id, Number(e.target.value) || 0)}
                    placeholder="0"
                    style={{
                      width: 64,
                      padding: '6px 8px',
                      borderRadius: 8,
                      border: '1px solid var(--divider-light)',
                      backgroundColor: 'var(--surface-bg)',
                      fontFamily: "'Inter', sans-serif",
                      fontSize: 20,
                      fontWeight: 500,
                      color: 'var(--text-primary)',
                      outline: 'none',
                      fontVariantNumeric: 'tabular-nums',
                    }}
                    onFocus={(e) => { e.currentTarget.style.borderColor = 'var(--accent-purple)'; }}
                    onBlur={(e) => { e.currentTarget.style.borderColor = 'var(--divider-light)'; }}
                  />
                  <span style={{ fontSize: 12, color: 'var(--text-muted)', fontFamily: "'Inter', sans-serif" }}>{m.unit}</span>
                </div>
                {/* Progress bar */}
                <div style={{ height: 3, borderRadius: 2, backgroundColor: 'var(--divider-light)', overflow: 'hidden', marginBottom: 4 }}>
                  <div style={{ height: '100%', width: `${pct}%`, backgroundColor: statusColor, borderRadius: 2, transition: 'width 400ms cubic-bezier(0.16,1,0.3,1)' }} />
                </div>
                <div className="flex justify-between">
                  <span style={{ fontSize: 10, color: 'var(--text-muted)', fontFamily: "'Inter', sans-serif" }}>
                    {Math.round(pct)}%
                  </span>
                  <span style={{ fontSize: 10, color: 'var(--text-muted)', fontFamily: "'Inter', sans-serif" }}>
                    target: {m.targetLabel}
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Derived Signals Row */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12, marginBottom: 20 }}>
          {[
            { label: 'Demand strength', value: demandStrength, color: demandStrength === 'High' ? '#1a7a63' : demandStrength === 'Medium' ? '#b87a0a' : '#c43c3c' },
            { label: 'Est. conversions', value: conversionEst.toString(), color: 'var(--text-primary)' },
            { label: 'Price acceptance', value: priceAcceptance, color: priceAcceptance === 'Strong' ? '#1a7a63' : priceAcceptance === 'Moderate' ? '#b87a0a' : '#c43c3c' },
          ].map((s) => (
            <div key={s.label} className="rounded-xl p-4 text-center" style={{ backgroundColor: 'var(--surface-input)' }}>
              <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 10, fontWeight: 300, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 6 }}>
                {s.label}
              </p>
              <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 18, fontWeight: 500, color: s.color, fontVariantNumeric: 'tabular-nums' }}>
                {s.value}
              </p>
            </div>
          ))}
        </div>

        {/* Verdict Card */}
        <div
          className="rounded-2xl text-center"
          style={{ padding: '32px 24px', backgroundColor: vc.bg, border: `1px solid ${vc.border}` }}
        >
          <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 10, fontWeight: 300, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 10 }}>
            Verdict
          </p>
          <p style={{ fontFamily: "'Instrument Serif', serif", fontSize: 28, fontWeight: 400, color: vc.color, letterSpacing: '-0.02em', lineHeight: 1.2, marginBottom: 12 }}>
            {vc.label}
          </p>
          <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 300, color: 'var(--text-secondary)', lineHeight: 1.7, maxWidth: 460, margin: '0 auto' }}>
            {reasoning}
          </p>
        </div>
      </div>

      {/* ── STEP 3: DISTRIBUTION CHANNELS (merged communities) ── */}
      <div style={{ marginBottom: 48 }}>
        <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.06em', marginBottom: 6 }}>
          3 · DISTRIBUTION CHANNELS
        </p>
        <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 300, color: 'var(--text-muted)', marginBottom: 14 }}>
          Track which channels you've shared on and their engagement.
        </p>

        {communities.length === 0 && !validationQuery.isFetching ? (
          <div className="rounded-xl p-6 text-center" style={{ backgroundColor: 'var(--surface-input)' }}>
            <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, color: 'var(--text-muted)' }}>
              No community channels found for this idea yet.
            </p>
          </div>
        ) : validationQuery.isFetching ? (
          <div className="rounded-xl p-6 text-center" style={{ backgroundColor: 'var(--surface-input)' }}>
            <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, color: 'var(--text-muted)' }}>
              Loading channels…
            </p>
          </div>
        ) : (
          <div className="rounded-xl overflow-hidden" style={{ border: '1px solid var(--divider-light)' }}>
            {/* Table header */}
            <div
              className="grid items-center px-4 py-2.5"
              style={{
                gridTemplateColumns: '1fr 90px 90px 100px',
                backgroundColor: 'var(--surface-input)',
                borderBottom: '1px solid var(--divider-light)',
              }}
            >
              <span style={{ fontFamily: "'Inter', sans-serif", fontSize: 11, fontWeight: 400, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Channel</span>
              <span style={{ fontFamily: "'Inter', sans-serif", fontSize: 11, fontWeight: 400, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Platform</span>
              <span style={{ fontFamily: "'Inter', sans-serif", fontSize: 11, fontWeight: 400, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Members</span>
              <span style={{ fontFamily: "'Inter', sans-serif", fontSize: 11, fontWeight: 400, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em', textAlign: 'center' }}>Status</span>
            </div>
            {/* Rows */}
            {communities.map((c) => {
              const isActive = activeChannels.has(c.id);
              return (
                <div
                  key={c.id}
                  className="grid items-center px-4 py-3 transition-colors duration-150"
                  style={{
                    gridTemplateColumns: '1fr 90px 90px 100px',
                    borderBottom: '1px solid var(--divider-light)',
                    backgroundColor: isActive ? 'rgba(45,139,117,0.03)' : 'var(--surface-card)',
                  }}
                >
                  <div>
                    <a
                      href={c.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 400, color: 'var(--text-primary)', textDecoration: 'none' }}
                    >
                      {c.name} <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>↗</span>
                    </a>
                    <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 11, fontWeight: 300, color: 'var(--text-muted)', marginTop: 2, lineHeight: 1.4 }}>
                      {c.rationale}
                    </p>
                  </div>
                  <span
                    className="rounded-full px-2 py-0.5 text-center"
                    style={{ fontSize: 10, fontWeight: 500, backgroundColor: c.platformColor, color: '#fff', width: 'fit-content' }}
                  >
                    {c.platform}
                  </span>
                  <span style={{ fontFamily: "'Inter', sans-serif", fontSize: 12, color: 'var(--text-secondary)', fontVariantNumeric: 'tabular-nums' }}>
                    {c.members}
                  </span>
                  <div style={{ textAlign: 'center' }}>
                    <button
                      onClick={() => toggleChannel(c.id)}
                      className="rounded-lg px-3 py-1 transition-all duration-200 active:scale-[0.96]"
                      style={{
                        fontSize: 11,
                        fontFamily: "'Inter', sans-serif",
                        fontWeight: 400,
                        backgroundColor: isActive ? 'rgba(45,139,117,0.1)' : 'var(--surface-input)',
                        color: isActive ? '#1a7a63' : 'var(--text-muted)',
                        border: 'none',
                        cursor: 'pointer',
                      }}
                    >
                      {isActive ? '✓ Shared' : 'Mark shared'}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* ── BOTTOM ACTIONS ── */}
      <div
        className="flex flex-wrap items-center gap-3 pt-8 pb-12"
        style={{ borderTop: '1px solid var(--divider)' }}
      >
        <button
          className="rounded-xl px-6 py-3 transition-all duration-200 active:scale-[0.97]"
          style={{
            fontFamily: "'Inter', sans-serif", fontSize: 14, fontWeight: 400,
            backgroundColor: 'var(--accent-purple)', color: '#FFFFFF',
            border: 'none', cursor: 'pointer',
          }}
        >
          Save validation results
        </button>
        <button
          className="rounded-xl px-5 py-3 transition-all duration-200 active:scale-[0.97]"
          style={{
            fontFamily: "'Inter', sans-serif", fontSize: 14, fontWeight: 400,
            backgroundColor: 'rgba(108,92,231,0.06)', color: 'var(--accent-purple)',
            border: 'none', cursor: 'pointer',
          }}
        >
          Export report
        </button>
      </div>
    </div>
  );
}
