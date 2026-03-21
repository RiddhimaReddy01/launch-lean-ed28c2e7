import { useState, useMemo } from 'react';
import { MOCK_METRICS, type MetricTarget } from '@/data/validate-mock';

type Verdict = 'awaiting' | 'go' | 'pivot' | 'kill';

function MetricCard({ metric, onChange }: { metric: MetricTarget & { actual: number }; onChange: (val: number) => void }) {
  const [hovered, setHovered] = useState(false);
  const pct = Math.min((metric.actual / metric.target) * 100, 100);
  const barColor = pct >= 100 ? '#2D8B75' : pct >= 50 ? '#D4880F' : 'var(--divider-light)';

  return (
    <div
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        padding: 24,
        borderRadius: 14,
        backgroundColor: '#FFFFFF',
        boxShadow: hovered ? '0 4px 16px rgba(0,0,0,0.06)' : '0 1px 3px rgba(0,0,0,0.04)',
        transition: 'box-shadow 200ms ease-out',
      }}
    >
      <div className="flex items-center justify-between" style={{ marginBottom: 16 }}>
        <span style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 400, color: 'var(--text-primary)' }}>
          {metric.label}
        </span>
        <span style={{ fontFamily: "'Inter', sans-serif", fontSize: 12, fontWeight: 300, color: 'var(--text-muted)' }}>
          Target: {metric.targetLabel}
        </span>
      </div>

      <div className="flex items-center" style={{ gap: 12, marginBottom: 14 }}>
        <input
          type="number"
          value={metric.actual || ''}
          onChange={(e) => onChange(Number(e.target.value) || 0)}
          placeholder="0"
          style={{
            width: 80, padding: '8px 12px', borderRadius: 8,
            border: '1px solid var(--divider-light)', backgroundColor: 'var(--surface-bg)',
            fontFamily: "'Inter', sans-serif", fontSize: 15, fontWeight: 400, color: 'var(--text-primary)',
            outline: 'none',
          }}
        />
        <span style={{ fontFamily: "'Inter', sans-serif", fontSize: 12, fontWeight: 300, color: 'var(--text-muted)' }}>
          {metric.unit}
        </span>
      </div>

      <div style={{ height: 4, borderRadius: 2, backgroundColor: 'var(--divider-light)', overflow: 'hidden' }}>
        <div style={{ height: '100%', width: `${pct}%`, backgroundColor: barColor, borderRadius: 2, transition: 'width 300ms ease-out' }} />
      </div>
      <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 11, fontWeight: 300, color: 'var(--text-muted)', marginTop: 6, textAlign: 'right' }}>
        {Math.round(pct)}% of target
      </p>
    </div>
  );
}

function DerivedSignals({ metrics }: { metrics: (MetricTarget & { actual: number })[] }) {
  const signups = metrics.find((m) => m.id === 'signups');
  const switchRate = metrics.find((m) => m.id === 'switch');
  const price = metrics.find((m) => m.id === 'price');

  const demandStrength = (signups?.actual || 0) >= 100 ? 'High' : (signups?.actual || 0) >= 50 ? 'Medium' : 'Low';
  const conversionRate = (signups?.actual || 0) > 0 ? Math.min(((switchRate?.actual || 0) / 100) * (signups?.actual || 0), signups?.actual || 0) : 0;
  const priceAcceptance = (price?.actual || 0) >= 10 ? 'Strong' : (price?.actual || 0) >= 7 ? 'Moderate' : 'Weak';

  const signals = [
    { label: 'Demand strength', value: demandStrength, color: demandStrength === 'High' ? '#2D8B75' : demandStrength === 'Medium' ? '#D4880F' : '#E05252' },
    { label: 'Est. conversions', value: Math.round(conversionRate).toString(), color: 'var(--text-primary)' },
    { label: 'Price acceptance', value: priceAcceptance, color: priceAcceptance === 'Strong' ? '#2D8B75' : priceAcceptance === 'Moderate' ? '#D4880F' : '#E05252' },
  ];

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, marginTop: 24 }}>
      {signals.map((s) => (
        <div key={s.label} style={{ padding: 20, borderRadius: 12, backgroundColor: 'var(--surface-bg)', textAlign: 'center' }}>
          <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 11, fontWeight: 300, color: 'var(--text-muted)', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            {s.label}
          </p>
          <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 18, fontWeight: 400, color: s.color }}>
            {s.value}
          </p>
        </div>
      ))}
    </div>
  );
}

function VerdictCard({ verdict, reasoning }: { verdict: Verdict; reasoning: string }) {
  const config: Record<Verdict, { label: string; color: string; bg: string }> = {
    awaiting: { label: 'Awaiting data', color: 'var(--text-muted)', bg: 'var(--surface-bg)' },
    go: { label: 'GO', color: '#2D8B75', bg: 'rgba(45,139,117,0.06)' },
    pivot: { label: 'PIVOT', color: '#D4880F', bg: 'rgba(212,136,15,0.06)' },
    kill: { label: 'NOT WORTH IT', color: '#E05252', bg: 'rgba(224,82,82,0.06)' },
  };
  const c = config[verdict];

  return (
    <div style={{ marginTop: 32, padding: 32, borderRadius: 16, backgroundColor: c.bg, textAlign: 'center' }}>
      <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 11, fontWeight: 300, color: 'var(--text-muted)', marginBottom: 12, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
        Verdict
      </p>
      <p style={{ fontFamily: "'Instrument Serif', serif", fontSize: 26, fontWeight: 400, color: c.color, letterSpacing: '-0.02em', marginBottom: 16 }}>
        {c.label}
      </p>
      <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 14, fontWeight: 300, color: 'var(--text-secondary)', lineHeight: 1.75, maxWidth: 500, margin: '0 auto' }}>
        {reasoning}
      </p>
    </div>
  );
}

export default function ExperimentDashboard() {
  const [metrics, setMetrics] = useState(MOCK_METRICS.map((m) => ({ ...m })));

  const updateMetric = (id: string, val: number) => {
    setMetrics((prev) => prev.map((m) => (m.id === id ? { ...m, actual: val } : m)));
  };

  const { verdict, reasoning } = useMemo(() => {
    const signups = metrics.find((m) => m.id === 'signups')?.actual || 0;
    const switchRate = metrics.find((m) => m.id === 'switch')?.actual || 0;
    const price = metrics.find((m) => m.id === 'price')?.actual || 0;
    const hasData = signups > 0 || switchRate > 0 || price > 0;

    if (!hasData) return { verdict: 'awaiting' as Verdict, reasoning: 'Enter your experiment results above to get a recommendation.' };

    if (signups >= 150 && switchRate >= 60 && price >= 8)
      return { verdict: 'go' as Verdict, reasoning: 'Strong demand signal with healthy price tolerance. The market is showing clear willingness to adopt. Move forward with confidence.' };

    if (signups < 30 && switchRate < 30)
      return { verdict: 'kill' as Verdict, reasoning: 'Low interest across channels. Consider a fundamentally different value proposition or target market.' };

    if (signups >= 80 && switchRate >= 40)
      return { verdict: 'pivot' as Verdict, reasoning: 'Moderate interest detected but not strong enough for a full launch. Consider refining your positioning, adjusting pricing, or targeting a narrower segment.' };

    if (price < 6 && signups > 50)
      return { verdict: 'pivot' as Verdict, reasoning: 'Strong interest but low price tolerance — consider repositioning your pricing strategy or reducing costs.' };

    return { verdict: 'pivot' as Verdict, reasoning: 'Mixed signals. Some interest exists but key metrics need improvement before investing further.' };
  }, [metrics]);

  return (
    <div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: 16 }}>
        {metrics.map((m) => (
          <MetricCard key={m.id} metric={m} onChange={(v) => updateMetric(m.id, v)} />
        ))}
      </div>

      <DerivedSignals metrics={metrics} />
      <VerdictCard verdict={verdict} reasoning={reasoning} />
    </div>
  );
}
