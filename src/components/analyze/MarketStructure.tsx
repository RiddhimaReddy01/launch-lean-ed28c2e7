import { MOCK_MARKET_STRUCTURE } from '@/data/analyze-mock';

function StructureIndicator({ label, value }: { label: string; value: string }) {
  const colors: Record<string, { bg: string; text: string }> = {
    low: { bg: 'rgba(45,139,117,0.06)', text: 'var(--accent-teal)' },
    medium: { bg: 'rgba(212,136,15,0.06)', text: 'var(--accent-amber)' },
    high: { bg: 'rgba(220,80,80,0.06)', text: '#dc5050' },
  };
  const c = colors[value] || colors.medium;

  return (
    <div
      className="rounded-[12px] p-5 cursor-default"
      style={{ backgroundColor: 'var(--surface-card)', boxShadow: '0 1px 3px rgba(0,0,0,0.04)' }}
    >
      <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.04em', marginBottom: 10 }}>
        {label}
      </p>
      <span
        className="rounded-[6px] px-3 py-1.5"
        style={{
          fontFamily: "'Inter', sans-serif",
          fontSize: 14,
          fontWeight: 400,
          backgroundColor: c.bg,
          color: c.text,
          display: 'inline-block',
        }}
      >
        {value}
      </span>
    </div>
  );
}

export default function MarketStructure() {
  const data = MOCK_MARKET_STRUCTURE;

  return (
    <div>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-12">
        <StructureIndicator label="SATURATION" value={data.saturation} />
        <StructureIndicator label="DIFFERENTIATION" value={data.differentiation} />
        <div
          className="rounded-[12px] p-5 sm:col-span-1"
          style={{ backgroundColor: 'var(--surface-card)', boxShadow: '0 1px 3px rgba(0,0,0,0.04)' }}
        >
          <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.04em', marginBottom: 10 }}>
            FRAGMENTATION
          </p>
          <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 400, color: 'var(--text-primary)', lineHeight: 1.5 }}>
            {data.fragmentation}
          </p>
        </div>
      </div>

      {/* Explanation */}
      <div
        className="rounded-[14px] p-6"
        style={{
          backgroundColor: 'rgba(59,130,246,0.03)',
          border: '1px solid rgba(59,130,246,0.08)',
        }}
      >
        <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.06em', marginBottom: 10, color: 'var(--accent-blue)' }}>
          MARKET READING
        </p>
        <p
          style={{
            fontFamily: "'Instrument Serif', serif",
            fontSize: 18,
            fontStyle: 'italic',
            color: 'var(--text-primary)',
            lineHeight: 1.6,
          }}
        >
          {data.explanation}
        </p>
      </div>
    </div>
  );
}
